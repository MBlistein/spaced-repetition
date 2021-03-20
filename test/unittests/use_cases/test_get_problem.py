import unittest
from unittest.mock import Mock, patch

import pandas as pd
from pandas.testing import assert_frame_equal

from spaced_repetition.domain.problem import Difficulty, ProblemCreator
from spaced_repetition.use_cases.get_problem import ProblemGetter
from spaced_repetition.use_cases.get_problem_log import ProblemLogGetter


class TestListProblems(unittest.TestCase):
    def setUp(self):
        self.problem = ProblemCreator.create(difficulty=Difficulty.EASY,
                                             problem_id=1,
                                             name='test_problem',
                                             tags=['tag_2', 'tag_1'],
                                             url='some_url.com')

    def test_get_problem_problems(self):
        p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())
        p_g.repo.get_problems.return_value = [self.problem]

        problem_df = p_g.get_problems(name_substr='aa', tag_names=['cc'])

        expected_df = pd.DataFrame(data=[{
            'name': 'test_problem',
            'problem_id': 1,
            'difficulty': Difficulty.EASY,
            'url': 'some_url.com',
            'tags': 'tag_1, tag_2'
        }])
        cols_in_order = sorted(expected_df.columns)

        # noinspection PyUnresolvedReferences
        p_g.repo.get_problems.assert_called_once_with(
            name_substr='aa', tag_names=['cc'])

        self.assertEqual(sorted(problem_df.columns),
                         sorted(expected_df.columns))

        assert_frame_equal(problem_df.reindex(columns=cols_in_order),
                           expected_df.reindex(columns=cols_in_order))

    def test_get_problems_none_found(self):
        p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())
        p_g.repo.get_problems.return_value = []

        self.assertTrue(p_g.get_problems().empty)

    @patch.object(ProblemLogGetter, 'get_problem_priorities'
    def test_get_prioritized_problems(self):
        p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())
        p_g.repo.get_problems.return_value = [self.problem]


    def test_get_prioritized_problems_none_found(self):
        p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())
        p_g.repo.get_problems.return_value = []

        self.assertTrue(p_g.get_prioritized_problems().empty)

#     @patch.object(ProblemGetter, 'get_prio_df')
#     def test_get_problem_df(self, mock_get_prio_df):
#         p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())
#         p_g.repo.get_problems = Mock()
#         p_g.repo.get_problems.return_value = [self.problem]
#
#         p_g.repo.get_problem_logs = Mock()
#         p_g.repo.get_problem_logs.return_value = [
#             ProblemLogCreator.create(
#                 last_log=None,
#                 problem_id=3,
#                 result=Result.NO_IDEA,
#                 timestamp=dt.datetime(2021, 1, 5, 10, tzinfo=gettz('UTC')))]
#
#         mock_get_prio_df.return_value = pd.DataFrame(data=[{
#             'problem_id': self.problem.problem_id,
#             'KS': 1.5
#         }])
#
#         expected_df = pd.DataFrame(data=[{
#             'KS': 1.5,
#             'difficulty': 'EASY',
#             'name': 'testname',
#             'problem_id': self.problem.problem_id,
#             'result': Result.NO_IDEA.value,
#             'RF': 2.11758e-22,
#             'tags': 'test-tag',
#             'ts_logged': dt.datetime(2021, 1, 5, 10),
#             'url': 'test-url'}])
#         print('33333333333333333333333333333333333333')
#         from tabulate import tabulate
#         print(tabulate(expected_df, headers='keys'))
#         print(sorted(expected_df.columns))
#         print('goooooooooooooooooooooooooooooooooooo')
#         got = p_g.get_problem_df(name_substr='a',
#                                               sorted_by=['b'],
#                                               tag_names=['c'])
#         print(sorted(got.columns))
#         print(tabulate(got, headers='keys'))
#
#         assert_frame_equal(p_g.get_problem_df(name_substr='a',
#                                               sorted_by=['b'],
#                                               tag_names=['c']),
#                            expected_df)
#         # noinspection PyUnresolvedReferences
#         p_g.repo.get_problems.assert_called_once_with(
#             name_substr='a', sorted_by=['b'], tag_names=['c'])
#
#
#
