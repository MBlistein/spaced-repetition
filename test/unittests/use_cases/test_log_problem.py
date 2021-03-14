
import unittest
from unittest.mock import Mock

from spaced_repetition.domain.problem import Difficulty, ProblemCreator
from spaced_repetition.use_cases.log_problem import ProblemLogger


TEST_PROBLEM = ProblemCreator.create_problem(
    name='testname',
    difficulty=Difficulty(1),
    problem_id=None,
    tags=['test-tag'],
    url='test-url')


class TestProblemAdder(unittest.TestCase):
    def test_add_log(self):
        # TODO: add interval and easiness
