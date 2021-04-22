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

        self.t1_p1_knowledge_data = {'ease': 1,
                                     'interval': 2,
                                     'KS': 3,
                                     'problem_id': 1,
                                     'result': 'NO_IDEA',
                                     'RF': 1,
                                     'tag': 'tag_1',
                                     'ts_logged': self.time_1}
        self.t2_p1_knowledge_data = {'ease': 3,
                                     'interval': 4,
                                     'KS': 3,
                                     'problem_id': 1,
                                     'result': 'SOLVED_OPTIMALLY_WITH_HINT',
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

    @patch.object(ProblemGetter, '_get_problems')
    @patch.object(ProblemLogGetter, 'get_knowledge_status')
    def test_list_problem_tag_combos(self, mock_get_knowledge_status,
                                     mock_get_problems):
        mock_get_problems.return_value = self.problem_df
        mock_get_knowledge_status.return_value = pd.DataFrame(
            self.knowledge_status_data)

        expected_result = self.problem_tag_combo_df

        mock_presenter = Mock()
        p_g = ProblemGetter(db_gateway=Mock(), presenter=mock_presenter)

        # call
        p_g.list_problem_tag_combos()

        mock_presenter.list_problem_tag_combos.assert_called_once()
        res = mock_presenter.list_problem_tag_combos.call_args[0][0]

        assert_frame_equal(expected_result, res, check_like=True)

    def test_denormalize_problems(self):
        expected_res = pd.DataFrame(data={
            'difficulty': [Difficulty.EASY] * 2,
            'problem': ['test_problem'] * 2,
            'problem_id': [1] * 2,
            'tag': ['tag_1', 'tag_2'],
            'url': ['some_url.com'] * 2})

        res = ProblemGetter._denormalize_problems(self.problem_df)

        assert_frame_equal(expected_res, res)

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

    def test_merge_problem_with_unlogged_combos(self):
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
    pass
    # @patch.object(ProblemLogGetter, 'get_problem_knowledge_scores')
    # @patch.object(ProblemGetter, '_get_problems')
    # def test_get_prioritized_problems(self, mock_get_problems,
    #                                   mock_get_problem_knowledge_scores):
    #     # prepare
    #     mock_get_problems.return_value = self.problem_df
    #     knowledge_score_df = pd.DataFrame(
    #         data=[self.problem_knowledge_data])
    #     mock_get_problem_knowledge_scores.return_value = knowledge_score_df
    #
    #     p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())
    #
    #     # call
    #     res = p_g.get_prioritized_problems(name_substr='aa',
    #                                        tags_all=['cc'])
    #
    #     # assert
    #     mock_get_problems.assert_called_once_with(name_substr='aa',
    #                                               tags_any=None,
    #                                               tags_all=['cc'])
    #     mock_get_problem_knowledge_scores.assert_called_once_with(
    #         problem_ids=[1])
    #
    #     assert_frame_equal(self.prioritized_problem, res, check_like=True)
    #
    # @patch.object(ProblemLogGetter, 'get_problem_knowledge_scores')
    # @patch.object(ProblemGetter, '_get_problems')
    # def test_get_prioritized_problems_new_problems(
    #         self, mock_get_problems, mock_get_problem_knowledge_scores):
    #     """ Assert that new problems have 'na' values for KS, etc. """
    #     # prepare
    #     new_problem_data = {
    #         'name': 'new_problem',
    #         'problem_id': 2,
    #         'difficulty': Difficulty.MEDIUM,
    #         'url': 'new_url.com',
    #         'tags': 'tag_1'}
    #     problem_df = pd.DataFrame(data=[self.problem_data, new_problem_data],
    #                               columns=self.problem_columns)
    #     mock_get_problems.return_value = problem_df
    #
    #     knowledge_score_df = pd.DataFrame(
    #         data=[self.problem_knowledge_data])
    #     mock_get_problem_knowledge_scores.return_value = knowledge_score_df
    #
    #     know_problem_data = self.problem_data.copy()
    #     know_problem_data.update(self.problem_knowledge_data)
    #     new_problem_data.update({
    #         'ts_logged': np.nan,
    #         'result': np.nan,
    #         'interval': np.nan,
    #         'ease': np.nan,
    #         'RF': np.nan,
    #         'KS': np.nan
    #     })
    #     expected_df = pd.DataFrame(data=[know_problem_data, new_problem_data])
    #
    #     p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())
    #
    #     # call
    #     res = p_g.get_prioritized_problems()
    #
    #     # assert
    #     assert_frame_equal(expected_df, res, check_like=True)
    #
    # def test_get_prioritized_problems_none_found(self):
    #     p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())
    #     p_g.repo.get_problems.return_value = []
    #
    #     expected_res = add_missing_columns(
    #         df=pd.DataFrame(), required_columns=[
    #             'difficulty', 'name', 'tags', 'url', 'problem_id', 'ts_logged',
    #             'result', 'ease', 'interval', 'RF', 'KS'])
    #
    #     with patch.object(ProblemLogGetter, 'get_problem_knowledge_scores') as \
    #             mock_ks_scores:
    #         mock_ks_scores.return_value = add_missing_columns(
    #             df=pd.DataFrame(),
    #             required_columns=['problem_id', 'ts_logged', 'result', 'ease',
    #                               'interval', 'RF', 'KS'])
    #
    #         res = p_g.get_prioritized_problems()
    #
    #         assert_frame_equal(expected_res, res)
