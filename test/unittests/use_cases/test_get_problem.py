
import unittest
from unittest.mock import Mock

from spaced_repetition.domain.problem import Difficulty, ProblemCreator
from spaced_repetition.use_cases.get_problem import ProblemGetter


TEST_PROBLEM = ProblemCreator.create_problem(
    name='testname',
    difficulty=Difficulty(1),
    problem_id=None,
    tags=['test-tag'],
    url='test-url')


class TestProblemGetter(unittest.TestCase):
    def setUp(self):
        self.p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())
        self.p_g.repo = Mock()
        self.p_g.repo.get_problems.return_value = 'repo_return_val'
        self.p_g.presenter = Mock()

    def test_get_problem_null_args(self):
        self.p_g.list_problems()

        self.p_g.presenter.list_problems.assert_called_once_with(
            'repo_return_val')
        self.p_g.repo.get_problems.assert_called_once_with(
            name_substr=None, sorted_by=None, tags=None)

    def test_get_problem_full_args(self):
        self.p_g.list_problems(name_substr='subs',
                               sorted_by=['arg1', 'arg2'],
                               tags=['tag1', 'tag2'])

        self.p_g.presenter.list_problems.assert_called_once_with(
            'repo_return_val')
        self.p_g.repo.get_problems.assert_called_once_with(
            name_substr='subs',
            sorted_by=['arg1', 'arg2'],
            tags=['tag1', 'tag2'])
