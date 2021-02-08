
import unittest
from unittest.mock import Mock

from spaced_repetition.domain.problem import Difficulty, ProblemCreator
from spaced_repetition.use_cases.add_problem import ProblemAdder


TEST_PROBLEM = ProblemCreator.create_problem(
    name='testname',
    difficulty=Difficulty(1),
    tags=['test-tag'],
    url='test-url')


class TestProblemAdder(unittest.TestCase):
    def test_add_problem(self):
        p_a = ProblemAdder(db_gateway=Mock(), presenter=Mock())
        p_a._assert_is_unique = Mock()
        p_a.add_problem(
            name=TEST_PROBLEM.name,
            difficulty=TEST_PROBLEM.difficulty,
            tags=TEST_PROBLEM.tags,
            url=TEST_PROBLEM.url)

        p_a._assert_is_unique.assert_called_once_with(problem=TEST_PROBLEM)
        p_a.repo.create_problem.assert_called_once_with(problem=TEST_PROBLEM)  # noqa

    def test_assert_is_unique_raises(self):
        p_a = ProblemAdder(db_gateway=Mock(), presenter=Mock())
        p_a.repo.get_problems.return_value = ['fake_problem']

        with self.assertRaises(ValueError) as context:
            p_a._assert_is_unique(problem=TEST_PROBLEM)

        self.assertEqual("Problem name 'testname' is not unique!",
                         str(context.exception))

    def test_assert_is_unique_ok(self):
        p_a = ProblemAdder(db_gateway=Mock(), presenter=Mock())
        p_a.repo.get_problems.return_value = []
        p_a._assert_is_unique(problem=TEST_PROBLEM)
