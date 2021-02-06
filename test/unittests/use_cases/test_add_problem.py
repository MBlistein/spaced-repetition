
import unittest
from unittest.mock import Mock

from spaced_repetition.domain.problem import ProblemCreator
from spaced_repetition.use_cases.add_problem import ProblemAdder


class TestProblemAdder(unittest.TestCase):
    def test_add_problem(self):
        problem = ProblemCreator.create_problem(
            name='testname',
            difficulty=1,
            tags=['test-tag'],
            link='test-link')

        p_a = ProblemAdder(db_gateway=Mock())
        p_a.add_problem(
            name='testname',
            difficulty=1,
            tags=['test-tag'],
            link='test-link')

        p_a.repo.create_problem.assert_called_once_with(problem=problem)  # noqa
