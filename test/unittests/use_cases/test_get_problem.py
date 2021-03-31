import datetime as dt
import unittest
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
from dateutil.tz import gettz
from pandas.testing import assert_frame_equal, assert_index_equal

from spaced_repetition.domain.problem import Difficulty, ProblemCreator
from spaced_repetition.domain.problem_log import Result
from spaced_repetition.use_cases.get_problem import ProblemGetter
from spaced_repetition.use_cases.get_problem_log import ProblemLogGetter
from spaced_repetition.use_cases.helpers_pandas import add_missing_columns


class TestListProblems(unittest.TestCase):
    def setUp(self):
        self.problem = ProblemCreator.create(difficulty=Difficulty.EASY,
                                             problem_id=1,
                                             name='test_problem',
                                             tags=['tag_2', 'tag_1'],
                                             url='some_url.com')

        self.problem_columns = [
            'difficulty', 'name', 'problem_id', 'tags', 'url']
        self.problem_data = {
            'difficulty': Difficulty.EASY,
            'name': 'test_problem',
            'problem_id': 1,
            'tags': 'tag_1, tag_2',
            'url': 'some_url.com'}
        self.problem_df = pd.DataFrame(data=[self.problem_data],
                                       columns=self.problem_columns)
        self.problem_knowledge_data = {
             'problem_id': 1,
             'ts_logged': dt.datetime(2021, 1, 1, tzinfo=gettz('UTC')),
             'result': Result.SOLVED_OPTIMALLY_SLOWER.value,
             'interval': 10,
             'ease': 2,
             'RF': 0.5,
             'KS': 2.0,
        }

        expected_data = self.problem_data.copy()
        expected_data.update(self.problem_knowledge_data)
        self.prioritized_problem = pd.DataFrame(data=[expected_data])

    def test_get_problems(self):
        p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())
        p_g.repo.get_problems.return_value = [self.problem]

        problem_df = p_g.get_problems(name_substr='aa',
                                      tags_any=['bb'],
                                      tags_all=['cc'])

        # noinspection PyUnresolvedReferences
        p_g.repo.get_problems.assert_called_once_with(
            name_substr='aa', tags_any=['bb'], tags_all=['cc'])

        assert_index_equal(problem_df.columns, self.problem_df.columns)
        assert_frame_equal(problem_df, self.problem_df)

    def test_get_problems_none_found(self):
        p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())
        p_g.repo.get_problems.return_value = []

        expected_df = add_missing_columns(df=pd.DataFrame(),
                                          required_columns=self.problem_columns)

        res = p_g.get_problems()

        assert_frame_equal(expected_df, res)

    @patch.object(ProblemLogGetter, 'get_problem_knowledge_scores')
    @patch.object(ProblemGetter, 'get_problems')
    def test_get_prioritized_problems(self, mock_get_problems,
                                      mock_get_problem_knowledge_scores):
        # prepare
        mock_get_problems.return_value = self.problem_df
        knowledge_score_df = pd.DataFrame(
            data=[self.problem_knowledge_data])
        mock_get_problem_knowledge_scores.return_value = knowledge_score_df

        p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())

        # call
        res = p_g.get_prioritized_problems(name_substr='aa',
                                           tags_all=['cc'])

        # assert
        mock_get_problems.assert_called_once_with(name_substr='aa',
                                                  tags_any=None,
                                                  tags_all=['cc'])
        mock_get_problem_knowledge_scores.assert_called_once_with(
            problem_ids=[1])

        assert_frame_equal(self.prioritized_problem, res, check_like=True)

    @patch.object(ProblemLogGetter, 'get_problem_knowledge_scores')
    @patch.object(ProblemGetter, 'get_problems')
    def test_get_prioritized_problems_new_problems(
            self, mock_get_problems, mock_get_problem_knowledge_scores):
        """ Assert that new problems have 'na' values for KS, etc. """
        # prepare
        new_problem_data = {
            'name': 'new_problem',
            'problem_id': 2,
            'difficulty': Difficulty.MEDIUM,
            'url': 'new_url.com',
            'tags': 'tag_1'}
        problem_df = pd.DataFrame(data=[self.problem_data, new_problem_data],
                                  columns=self.problem_columns)
        mock_get_problems.return_value = problem_df

        knowledge_score_df = pd.DataFrame(
            data=[self.problem_knowledge_data])
        mock_get_problem_knowledge_scores.return_value = knowledge_score_df

        know_problem_data = self.problem_data.copy()
        know_problem_data.update(self.problem_knowledge_data)
        new_problem_data.update({
            'ts_logged': np.nan,
            'result': np.nan,
            'interval': np.nan,
            'ease': np.nan,
            'RF': np.nan,
            'KS': np.nan
        })
        expected_df = pd.DataFrame(data=[know_problem_data, new_problem_data])

        p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())

        # call
        res = p_g.get_prioritized_problems()

        # assert
        assert_frame_equal(expected_df, res, check_like=True)

    def test_get_prioritized_problems_none_found(self):
        p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())
        p_g.repo.get_problems.return_value = []

        expected_res = add_missing_columns(
            df=pd.DataFrame(), required_columns=[
                'difficulty', 'name', 'tags', 'url', 'problem_id', 'ts_logged',
                'result', 'ease', 'interval', 'RF', 'KS'])

        with patch.object(ProblemLogGetter, 'get_problem_knowledge_scores') as \
                mock_ks_scores:
            mock_ks_scores.return_value = add_missing_columns(
                df=pd.DataFrame(),
                required_columns=['problem_id', 'ts_logged', 'result', 'ease',
                                  'interval', 'RF', 'KS'])

            res = p_g.get_prioritized_problems()

            assert_frame_equal(expected_res, res)
