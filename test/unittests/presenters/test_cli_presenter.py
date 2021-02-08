
import unittest

from spaced_repetition.domain.problem import Difficulty, ProblemCreator
from spaced_repetition.presenters.cli_presenter import CliPresenter


class TestCliPresenter(unittest.TestCase):
    def test_problem_confirmation_txt(self):
        problem = ProblemCreator.create_problem(
            name='testname',
            difficulty=Difficulty(1),
            tags=['test-tag'],
            link='test-link')
        self.assertEqual("Created Problem 'testname' (difficulty 'EASY', "
                         "tags: test-tag)",
                         CliPresenter._problem_confirmation_txt(problem=problem))
