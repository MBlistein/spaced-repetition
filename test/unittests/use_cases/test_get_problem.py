import datetime as dt
import unittest
from unittest.mock import Mock, patch

import pandas as pd
from dateutil.tz import gettz
from pandas.testing import assert_frame_equal

from spaced_repetition.domain.problem import Difficulty, ProblemCreator
from spaced_repetition.domain.problem_log import Result
from spaced_repetition.use_cases.get_problem import ProblemGetter
from spaced_repetition.use_cases.get_problem_log import ProblemLogGetter


class TestListProblems(unittest.TestCase):
    def setUp(self):
        self.problem = ProblemCreator.create(difficulty=Difficulty.EASY,
                                             problem_id=1,
                                             name='test_problem',
                                             tags=['tag_2', 'tag_1'],
                                             url='some_url.com')

        self.problem_df = pd.DataFrame(data=[{
            'name': 'test_problem',
            'problem_id': 1,
            'difficulty': Difficulty.EASY,
            'url': 'some_url.com',
            'tags': 'tag_1, tag_2'
        }])

    def test_get_problems(self):
        p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())
        p_g.repo.get_problems.return_value = [self.problem]

        problem_df = p_g.get_problems(name_substr='aa', tag_names=['cc'])

        expected_df = self.problem_df
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

    @patch.object(ProblemLogGetter, 'get_problem_knowledge_scores')
    @patch.object(ProblemGetter, 'get_problems')
    def test_get_prioritized_problems(self, mock_get_problems,
                                      mock_get_problem_knowledge_scores):
        mock_get_problems.return_value = self.problem_df
        knowledge_score_df = pd.DataFrame(data=[{
            'problem_id': 1,
            'ts_logged': dt.datetime(2021, 1, 1, tzinfo=gettz('UTC')),
            'result': Result.SOLVED_OPTIMALLY_SLOWER.value,
            'interval': 10,
            'ease': 2,
            'RF': 0.5,
            'KS': 2.0}])
        mock_get_problem_knowledge_scores.return_value = knowledge_score_df
        p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())

        res = p_g.get_prioritized_problems(name_substr='aa',
                                           sorted_by=['bb'],
                                           tag_names=['cc'])

        expected_res = knowledge_score_df
        expected_res['difficulty'] = self.problem.difficulty
        expected_res['name'] = self.problem.name
        expected_res['tags'] = 'tag_1, tag_2'
        expected_res['url'] = self.problem.url
        ordered_cols = sorted(expected_res.columns)

        mock_get_problems.assert_called_once_with(name_substr='aa',
                                                  tag_names=['cc'])
        mock_get_problem_knowledge_scores.assert_called_once_with(
            problem_ids=[1])

        self.assertEqual(ordered_cols, sorted(res.columns))

        assert_frame_equal(expected_res.reindex(columns=ordered_cols),
                           res.reindex(columns=ordered_cols))

    def test_get_prioritized_problems_none_found(self):
        p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())
        p_g.repo.get_problems.return_value = []

        self.assertTrue(p_g.get_prioritized_problems().empty)
