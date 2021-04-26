import copy
import datetime as dt
import unittest
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal, assert_index_equal

from spaced_repetition.domain.problem import Difficulty, ProblemCreator
from spaced_repetition.domain.tag import TagCreator
from spaced_repetition.use_cases.get_problem import ProblemGetter
from spaced_repetition.use_cases.get_problem_log import ProblemLogGetter
from spaced_repetition.use_cases.helpers_pandas import add_missing_columns


""" some day these tests should be regrouped by purpose to de-duplicate data"""


class TestListProblemTagCombos(unittest.TestCase):
    def setUp(self):
        self.time_1 = dt.datetime(2021, 1, 10, 1)
        self.time_2 = dt.datetime(2021, 1, 10, 5)
        self.tag_1 = TagCreator.create(name='tag_1')
        self.tag_2 = TagCreator.create(name='tag_2')
        self.problem = ProblemCreator.create(difficulty=Difficulty.EASY,
                                             problem_id=1,
                                             name='test_problem',
                                             tags=['tag_2', 'tag_1'],
                                             url='some_url.com')

        self.problem_columns = [
            'difficulty', 'problem', 'problem_id', 'tags', 'url']
        self.problem_data = {
            'difficulty': Difficulty.EASY,
            'problem': 'test_problem',
            'problem_id': 1,
            'tags': 'tag_1, tag_2',
            'url': 'some_url.com'}
        self.problem_df = pd.DataFrame(data=[self.problem_data],
                                       columns=self.problem_columns)
        self.unlogged_problem_data = {
            'difficulty': Difficulty.EASY,
            'problem': 'unattempted_problem',
            'problem_id': 2,
            'tags': 'unattempted_tag'}
        self.unlogged_problem_with_logged_tag_data = {
            'difficulty': Difficulty.EASY,
            'problem': 'unattempted_problem_with_logged_tag',
            'problem_id': 3,
            'tags': self.tag_1.name}

        self.t1_p1_knowledge_data = {'ease': 1,
                                     'interval': 2,
                                     'KS': 5,
                                     'problem_id': 1,
                                     'result': 'KNEW_BY_HEARt',
                                     'RF': 1,
                                     'tag': 'tag_1',
                                     'ts_logged': self.time_1}
        self.t2_p1_knowledge_data = {'ease': 3,
                                     'interval': 4,
                                     'KS': 0,
                                     'problem_id': 1,
                                     'result': 'NO_IDEA',
                                     'RF': 1,
                                     'tag': 'tag_2',
                                     'ts_logged': self.time_2}
        self.knowledge_status_data = [self.t1_p1_knowledge_data,
                                      self.t2_p1_knowledge_data]

        # build problem-tag-combo-df: knowledge data merged with problem data
        ks_data = copy.deepcopy(self.knowledge_status_data)
        for ks_dict in ks_data:
            ks_dict.update({k: v for k, v in self.problem_data.items() if k != 'tags'})
        self.problem_tag_combo_df = pd.DataFrame(ks_data)

    def test_get_problems(self):
        mock_repo = Mock()
        mock_repo.get_problems.return_value = [self.problem]
        p_g = ProblemGetter(db_gateway=mock_repo, presenter=Mock())

        problem_df = p_g._get_problems(name_substr='aa',
                                       tags_any=['bb'],
                                       tags_all=['cc'])

        expected_result = self.problem_df

        mock_repo.get_problems.assert_called_once_with(
            name_substr='aa', tags_any=['bb'], tags_all=['cc'])

        assert_frame_equal(expected_result, problem_df,
                           check_like=True)  # no particular column order

    def test_get_problems_none_found(self):
        p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())
        p_g.repo.get_problems.return_value = []

        expected_df = add_missing_columns(df=pd.DataFrame(),
                                          required_columns=self.problem_columns)

        res = p_g._get_problems()

        assert_frame_equal(expected_df, res)

    @patch.object(ProblemGetter, 'get_knowledge_status')
    @patch.object(ProblemGetter, '_filter_tags')
    def test_list_problem_tag_combos(self, mock_filter_args,
                                     mock_get_knowledge_status):
        mock_get_knowledge_status.return_value = self.problem_tag_combo_df
        mock_filter_args.return_value = 'fake_res'

        mock_presenter = Mock()
        p_g = ProblemGetter(db_gateway=Mock(), presenter=mock_presenter)

        # call
        p_g.list_problem_tag_combos(tag_substr='test_substr')

        mock_get_knowledge_status.assert_called_once()
        call_df = mock_filter_args.call_args[1]['df']
        filter_str = mock_filter_args.call_args[1]['tag_substr']
        assert_frame_equal(call_df, self.problem_tag_combo_df.sort_values('KS'))
        self.assertEqual(filter_str, 'test_substr')
        mock_presenter.list_problem_tag_combos.assert_called_once_with(
            'fake_res')

    @patch.object(ProblemGetter, '_get_problems')
    @patch.object(ProblemLogGetter, 'get_last_log_per_problem_tag_combo')
    def test_get_knowledge_status(self, mock_log_data_getter, mock_get_problems):
        """ test that all data is retrieved, including unlogged problems """
        problem_df = pd.DataFrame(data={
            'difficulty': [Difficulty.EASY] * 3,
            'problem': ['problem_1', 'unlogged_problem', 'unlogged_problem_with_logged_tag'],
            'problem_id': [1, 2, 3],
            'tags': ['tag_1, tag_2', 'unlogged_tag', 'tag_1'],
            'url': ['some_url.com'] * 3})

        # problem 1 has been logged with 2 tags
        log_df = pd.DataFrame(data={
            'ease': [1] * 2,
            'interval': [2] * 2,
            'KS': [5] * 2,
            'problem_id': [1] * 2,
            'result': ['KNEW_BY_HEART'] * 2,
            'RF': [1] * 2,
            'tag': ['tag_1', 'tag_2'],
            'ts_logged': [self.time_1] * 2})

        expected_res = pd.DataFrame(data={
            'difficulty': [Difficulty.EASY] * 4,
            'problem': ['problem_1', 'problem_1', 'unlogged_problem', 'unlogged_problem_with_logged_tag'],
            'problem_id': [1, 1, 2, 3],
            'url': ['some_url.com'] * 4,
            'ease': [1, 1, np.nan, np.nan],
            'interval': [2, 2, np.nan, np.nan],
            'KS': [5, 5, np.nan, np.nan],
            'result': ['KNEW_BY_HEART', 'KNEW_BY_HEART', np.nan, np.nan],
            'RF': [1, 1, np.nan, np.nan],
            'tag': ['tag_1', 'tag_2', 'unlogged_tag', 'tag_1'],
            'ts_logged': [self.time_1, self.time_1, np.nan, np.nan]})

        mock_get_problems.return_value = problem_df
        mock_log_data_getter.return_value = log_df
        p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())

        # call
        res = p_g.get_knowledge_status()

        assert_frame_equal(expected_res, res, check_like=True)

    def test_merge_problem_and_log_data_one_to_one(self):
        prob_df = pd.DataFrame({'problem': ['problem'] * 2,
                                'tag': ['tag_1', 'tag_2'],
                                'problem_id': [1] * 2})
        log_df = pd.DataFrame({'problem_id': [1] * 2,
                               'tag': ['tag_1', 'tag_2'],
                               'result': ['result_1', 'result_2']})
        expected_res = pd.DataFrame(
            {'problem': ['problem'] * 2,
             'tag': ['tag_1', 'tag_2'],
             'problem_id': [1] * 2,
             'result': ['result_1', 'result_2']})

        res = ProblemGetter._merge_problem_and_log_data(problem_data=prob_df,
                                                        log_data=log_df)

        assert_frame_equal(expected_res, res)

    def test_merge_problem_and_log_data_one_to_many(self):
        prob_df = pd.DataFrame({'problem': ['problem'],
                                'tag': ['tag_1'],
                                'problem_id': [1]})
        log_df = pd.DataFrame({'problem_id': [1] * 2,
                               'tag': ['tag_1', 'tag_1'],
                               'result': ['result_1', 'result_2']})
        expected_res = pd.DataFrame(
            {'problem': ['problem'] * 2,
             'tag': ['tag_1', 'tag_1'],
             'problem_id': [1] * 2,
             'result': ['result_1', 'result_2']})

        res = ProblemGetter._merge_problem_and_log_data(problem_data=prob_df,
                                                        log_data=log_df)

        assert_frame_equal(expected_res, res)

    def test_merge_problem_with_unlogged_problems(self):
        prob_df = pd.DataFrame({'problem': ['problem'] * 2,
                                'tag': ['tag_1', 'tag_2'],
                                'problem_id': [1] * 2})
        log_df = pd.DataFrame({'problem_id': [1],
                               'tag': ['tag_1'],
                               'result': ['result_1']})
        expected_res = pd.DataFrame(
            {'problem': ['problem'] * 2,
             'tag': ['tag_1', 'tag_2'],
             'problem_id': [1] * 2,
             'result': ['result_1', np.nan]})

        res = ProblemGetter._merge_problem_and_log_data(problem_data=prob_df,
                                                        log_data=log_df)

        assert_frame_equal(expected_res, res)

    def test_filter_tags(self):
        tag_2_ks_data = self.t2_p1_knowledge_data.copy()
        tag_2_ks_data.update(self.problem_data)
        tag_2_ks_data.pop('tags')
        expected_result = pd.DataFrame(data=tag_2_ks_data, index=[1])

        res = ProblemGetter._filter_tags(self.problem_tag_combo_df,
                                         tag_substr='g_2')

        assert_frame_equal(expected_result, res)


class TestListProblems(unittest.TestCase):
    def setUp(self):
        self.time_1 = dt.datetime(2021, 1, 10, 1)

    def test_aggregate_problems(self):
        knowledge_status = pd.DataFrame(data={
            'difficulty': [Difficulty.EASY] * 4,
            'problem': ['problem_1', 'problem_1', 'unlogged_problem', 'unlogged_problem_with_logged_tag'],
            'problem_id': [1, 1, 2, 3],
            'url': ['some_url.com'] * 4,
            'ease': [1, 1, np.nan, np.nan],
            'interval': [2, 2, np.nan, np.nan],
            'KS': [5, 5, np.nan, np.nan],
            'result': ['KNEW_BY_HEART', 'KNEW_BY_HEART', np.nan, np.nan],
            'RF': [1, 1, np.nan, np.nan],
            'tag': ['tag_1', 'tag_2', 'unlogged_tag', 'tag_1'],
            'ts_logged': [self.time_1, self.time_1, np.nan, np.nan]})

        expected_result = pd.DataFrame(data={
            'problem_id': [1, 2, 3],
            'KS': [5., 0., 0.],
            'RF': [1, np.nan, np.nan]})

        p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())

        # call
        res = p_g.aggregate_problems(knowledge_status)

        assert_frame_equal(expected_result, res, check_like=True)

    @patch.object(ProblemGetter, '_get_problems')
    @patch.object(ProblemGetter, 'get_knowledge_status')
    def test_get_knowledge_status(self, mock_get_knowledge_status, mock_get_problems):
        """ test that all data is retrieved, including unlogged problems """
        problem_df = pd.DataFrame(data={
            'difficulty': [Difficulty.EASY] * 2,
            'problem': ['problem_1', 'unlogged_problem'],
            'problem_id': [1, 2],
            'tags': ['tag_1, tag_2', 'unlogged_tag'],
            'url': ['some_url.com'] * 2})

        knowledge_status = pd.DataFrame(data={
            'difficulty': [Difficulty.EASY] * 3,
            'problem': ['problem_1', 'problem_1', 'unlogged_problem'],
            'problem_id': [1, 1, 2],
            'url': ['some_url.com'] * 3,
            'ease': [1, 1, np.nan],
            'interval': [2, 2, np.nan],
            'KS': [5, 5, np.nan],
            'result': ['KNEW_BY_HEART', 'KNEW_BY_HEART', np.nan],
            'RF': [1, 1, np.nan],
            'tag': ['tag_1', 'tag_2', 'unlogged_tag'],
            'ts_logged': [self.time_1, self.time_1, np.nan]})

        expected_res = pd.DataFrame(data={
            'difficulty': [Difficulty.EASY] * 2,
            'problem': ['problem_1', 'unlogged_problem'],
            'problem_id': [1, 2],
            'url': ['some_url.com'] * 2,
            'KS': [5., 0.],
            'RF': [1, np.nan],
            'tags': ['tag_1, tag_2', 'unlogged_tag']})

        mock_get_problems.return_value = problem_df
        mock_get_knowledge_status.return_value = knowledge_status
        p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())

        # call
        p_g.list_problems()

        res = p_g.presenter.list_problems.call_args[0][0]

        assert_frame_equal(expected_res, res, check_like=True)

