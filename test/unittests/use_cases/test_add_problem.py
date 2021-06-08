
import unittest
from unittest.mock import Mock, patch

from spaced_repetition.domain.problem import Difficulty, ProblemCreator
from spaced_repetition.domain.tag import TagCreator
from spaced_repetition.use_cases.add_problem import ProblemAdder
from spaced_repetition.use_cases.get_tag import TagGetter


# pylint: disable=protected-access


class TestProblemAdder(unittest.TestCase):
    def setUp(self) -> None:
        self.test_tag = TagCreator.create(name='test-tag',
                                          experience_target=5)
        self.test_problem = ProblemCreator.create(
            name='testname',
            difficulty=Difficulty(1),
            problem_id=None,
            tags=[self.test_tag],
            url='test-url')

    @patch.object(TagGetter, 'get_existing_tags')
    def test_add_problem(self, mock_get_existing_tags):
        mock_get_existing_tags.return_value = [self.test_tag]
        p_a = ProblemAdder(db_gateway=Mock(), presenter=Mock())
        p_a._assert_is_unique = Mock()
        p_a.add_problem(
            name=self.test_problem.name,
            difficulty=self.test_problem.difficulty,
            tags=self.test_problem.tags,
            url=self.test_problem.url)

        p_a._assert_is_unique.assert_called_once_with(problem=self.test_problem)
        p_a.repo.create_problem.assert_called_once_with(problem=self.test_problem)  # noqa

    def test_assert_is_unique_raises(self):
        p_a = ProblemAdder(db_gateway=Mock(), presenter=Mock())
        p_a.repo.problem_exists.return_value = True

        with self.assertRaises(ValueError) as context:
            p_a._assert_is_unique(problem=self.test_problem)

        self.assertEqual("Problem name 'testname' is not unique!",
                         str(context.exception))

    def test_assert_is_unique(self):
        p_a = ProblemAdder(db_gateway=Mock(), presenter=Mock())
        p_a.repo.problem_exists.return_value = False
        p_a._assert_is_unique(problem=self.test_problem)
