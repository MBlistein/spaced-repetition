import datetime as dt
import unittest
from unittest.mock import Mock

from spaced_repetition.domain.problem import Difficulty, ProblemCreator
from spaced_repetition.domain.problem_log import ProblemLogCreator, Result
from spaced_repetition.domain.tag import TagCreator
from spaced_repetition.use_cases.log_problem import ProblemLogger


class TestProblemLogger(unittest.TestCase):
    def setUp(self) -> None:
        self.tag_1 = TagCreator.create(name='tag_1')
        self.tag_2 = TagCreator.create(name='tag_2')
        self.problem = ProblemCreator.create(name='problem_1',
                                             difficulty=Difficulty.MEDIUM,
                                             problem_id=1,
                                             tags=[self.tag_1])
        self.pl_1 = ProblemLogCreator.create(
            problem_id=self.problem.problem_id,
            result=Result.NO_IDEA,
            tags=[self.tag_1],
            timestamp=dt.datetime(2021, 3, 19))
        self.pl_2 = ProblemLogCreator.create(
            problem_id=self.problem.problem_id,
            result=Result.NO_IDEA,
            tags=[self.tag_2],
            timestamp=dt.datetime(2021, 3, 20))

    def test_log_problem(self):
        repo = Mock()
        repo.get_problems.return_value = [self.problem]
        repo.get_tags.return_value = [self.tag_2]
        p_l = ProblemLogger(db_gateway=repo, presenter=Mock())

        p_l.log_problem(
            comment=self.pl_2.comment,
            problem_name=self.problem.name,
            result=self.pl_2.result,
            tags=[self.tag_2.name])

        repo.create_problem_log.assert_called_once()
        called_with = repo.create_problem_log.call_args[1]['problem_log']
        self.assertEqual(called_with.tags, [self.tag_2])
        self.assertEqual(called_with.problem_id, self.problem.problem_id)
        p_l.presenter.confirm_problem_logged.assert_called_once()  # noqa

    def test_log_problem_raises_problem_does_not_exist(self):
        repo = Mock()
        repo.get_problems.return_value = []
        p_l = ProblemLogger(db_gateway=repo, presenter=Mock())

        with self.assertRaises(ValueError) as context:
            p_l.log_problem(
                comment=self.pl_2.comment,
                problem_name='non_existing_problem_name',
                result=self.pl_2.result,
                tags=[self.tag_2.name])

        self.assertEqual(str(context.exception),
                         "Problem with name 'non_existing_problem_name' does "
                         "not exist, try searching for similar problems.")

    def test_log_problem_raises_tags_dont_exist(self):
        repo = Mock()
        repo.get_problems.return_value = [self.problem]
        repo.get_tags.return_value = [self.tag_2]
        p_l = ProblemLogger(db_gateway=repo, presenter=Mock())

        with self.assertRaises(ValueError) as context:
            p_l.log_problem(
                comment=self.pl_2.comment,
                problem_name=self.problem.name,
                result=self.pl_2.result,
                tags=[self.tag_2.name, 'non_existing_tag'])

        self.assertEqual(
            str(context.exception),
            "The following tag names don't exist: {'non_existing_tag'}")
