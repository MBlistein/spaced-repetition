import datetime as dt
import unittest
from unittest.mock import patch, Mock

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal


from spaced_repetition.domain.problem import Difficulty
from spaced_repetition.domain.tag import TagCreator
from spaced_repetition.use_cases.get_tag import TagGetter
from spaced_repetition.use_cases.get_problem import ProblemGetter


class TestGetTags(unittest.TestCase):
    def test_get_tags(self):
        tag_1 = TagCreator.create(name='tag_1')
        tag_2 = TagCreator.create(name='tag_2')

        tag_getter = TagGetter(db_gateway=Mock(), presenter=Mock())
        tag_getter.repo.get_tags.return_value = [tag_1, tag_2]

        expected_df = pd.DataFrame(data={'tag': ['tag_1', 'tag_2'],
                                         'tag_id': [None, None]})

        tag_df = tag_getter.get_tags()

        assert_frame_equal(expected_df, tag_df)

    def test_get_tags_no_data(self):
        tag_getter = TagGetter(db_gateway=Mock(), presenter=Mock())
        tag_getter.repo.get_tags.return_value = []

        tag_df = tag_getter.get_tags()

        self.assertTrue(tag_df.empty)
        self.assertEqual(['tag', 'tag_id'], tag_df.columns.to_list())


class TestGetPrioritizedTags(unittest.TestCase):
    def setUp(self) -> None:
        self.prob_data_easy_1 = {
            'name': 'easy_problem_1',
            'difficulty': Difficulty.EASY,
            'KS': 3,
            'tag': 'tag_1',
            'ts_logged': dt.datetime(2021, 1, 1, 10)}

        self.prob_data_easy_2 = {
            'name': 'easy_problem_2',
            'difficulty': Difficulty.EASY,
            'KS': 5,
            'tag': 'tag_1',
            'ts_logged': dt.datetime(2021, 1, 1, 10)}

        self.prob_data_medium = {
            'name': 'medium_problem',
            'difficulty': Difficulty.MEDIUM,
            'KS': 2,
            'tag': 'tag_1',
            'ts_logged': dt.datetime(2021, 1, 1, 10)}
        self.prob_data_tag_2_easy = {
            'name': 'easy_problem_3',
            'difficulty': Difficulty.EASY,
            'KS': 5,
            'tag': 'tag_2',
            'ts_logged': dt.datetime(2021, 1, 1, 10)}

        self.prob_data_tag_2_medium = {
            'name': 'medium_problem_2',
            'difficulty': Difficulty.MEDIUM,
            'KS': 4,
            'tag': 'tag_2',
            'ts_logged': dt.datetime(2021, 1, 1, 10)}

        self.prob_data_tag_2_hard = {
            'name': 'medium_problem_2',
            'difficulty': Difficulty.HARD,
            'KS': 3,
            'tag': 'tag_2',
            'ts_logged': dt.datetime(2021, 1, 1, 10)}

        self.prob_data_never_done = {
            'name': 'new_problem',
            'difficulty': Difficulty.HARD,
            'KS': np.nan,
            'tag': 'tag_new',
            'ts_logged': np.nan}

        self.empty_problem_df = pd.DataFrame(columns=[
            'difficulty', 'name', 'tag', 'url', 'problem_id', 'ts_logged',
            'result', 'ease', 'interval', 'RF', 'KS'])

        self.empty_tag_df = pd.DataFrame(columns=[
            'tags', 'experience', 'KW (weighted avg)', 'num_problems',
            'priority'])

    def test_prioritize(self):
        test_df = pd.DataFrame(data=[
            self.prob_data_easy_1,
            self.prob_data_easy_2,
            self.prob_data_medium])

        expected_res = pd.Series(
            data={
                'KS (weighted avg)': 0.25 * 4 + 0.5 * 2,
                'experience': 0.6,
                'num_problems': 3,
                'priority': 1.2},
            dtype='object')

        res = TagGetter._prioritize(group_df=test_df)

        assert_series_equal(expected_res,
                            res.reindex(index=expected_res.index))

    def test_prioritize_empty_data(self):
        expected_res = pd.Series(index=[
            'experience', 'KW (weighted avg)', 'num_problems', 'priority'],
            dtype='object')

        res = TagGetter._prioritize(group_df=self.empty_problem_df)

        assert_series_equal(expected_res, res)

    def test_prioritize_tags(self):
        test_df = pd.DataFrame(data=[
            self.prob_data_easy_1,
            self.prob_data_easy_2,
            self.prob_data_medium,
            self.prob_data_tag_2_easy,
            self.prob_data_tag_2_medium,
            self.prob_data_tag_2_hard,
            self.prob_data_never_done])

        expected_res = pd.DataFrame(data=[
            {'tag': 'tag_1',
             'KS (weighted avg)': 2.0,
             'experience': 0.6,
             'num_problems': 3,
             'priority': 1.2},
            {'tag': 'tag_2',
             'KS (weighted avg)': 4.0,
             'experience': 0.6,
             'num_problems': 3,
             'priority': 2.4},
            {'tag': 'tag_new',
             'KS (weighted avg)': 0.0,
             'experience': 0.0,
             'num_problems': 1,
             'priority': 0.0}
        ])

        res = TagGetter._prioritize_tags(tag_data=test_df)

        assert_frame_equal(expected_res, res,
                           check_like=True)

    def test_prioritize_tags_empty_data(self):
        res = TagGetter._prioritize_tags(tag_data=self.empty_problem_df)

        assert_frame_equal(self.empty_tag_df, res)

    @patch.object(TagGetter, 'get_tags')
    @patch.object(TagGetter, '_get_problems_per_tag')
    @patch.object(TagGetter, '_prioritize_tags')
    def test_get_prioritized_tags(self, mock_prioritize_tags,
                                  mock_get_problems_per_tag, mock_get_tags):
        # prepare
        mock_prioritize_tags.return_value = 'fake_prio_df'
        mock_get_problems_per_tag.return_value = pd.DataFrame(data={
            'tag': ['tag_1', 'tag_2'], 'some_info': [1, 2]})
        mock_get_tags.return_value = pd.DataFrame(data={
            'tag': ['tag_1', 'tag_2'], 'tag_id': [1, 2]})

        tag_getter = TagGetter(db_gateway=Mock(), presenter=Mock())

        expected_merge_df = pd.DataFrame(data={
            'tag': ['tag_1', 'tag_2'], 'tag_id': [1, 2], 'some_info': [1, 2]})

        # call
        res = tag_getter.get_prioritized_tags(sub_str='test_str')

        # assert
        mock_get_tags.assert_called_once_with(sub_str='test_str')
        mock_get_problems_per_tag.assert_called_once_with(
            filter_tags=['tag_1', 'tag_2'])

        merge_res = mock_prioritize_tags.call_args.kwargs['tag_data']
        assert_frame_equal(expected_merge_df, merge_res)
        mock_prioritize_tags.assert_called_once()
        self.assertEqual('fake_prio_df', res)

    @patch.object(TagGetter, 'get_tags')
    @patch.object(TagGetter, '_get_problems_per_tag')
    def test_get_prioritized_tags_no_data(
            self, mock_get_problems_per_tag, mock_get_tags):
        # prepare
        mock_get_problems_per_tag.return_value = self.empty_problem_df
        mock_get_tags.return_value = pd.DataFrame(
            columns=['tag', 'tag_id'])

        tag_getter = TagGetter(db_gateway=Mock(), presenter=Mock())

        # call
        res = tag_getter.get_prioritized_tags()

        # assert
        mock_get_tags.assert_called_once_with(sub_str=None)
        mock_get_problems_per_tag.assert_called_once_with(filter_tags=None)
        assert_frame_equal(self.empty_tag_df, res)

    @patch.object(ProblemGetter, 'get_prioritized_problems')
    def test_get_problems_per_tag(self, mock_get_prioritized_problems):
        mock_get_prioritized_problems.return_value = pd.DataFrame(data=[
            {'tags': 'tag_1, tag_2',
             'name': 'prob_1'},
            {'tags': 'tag_2',
             'name': 'prob_2'},
        ])
        expected_df = pd.DataFrame(data=[
            {'tag': 'tag_1',
             'name': 'prob_1'},
            {'tag': 'tag_2',
             'name': 'prob_1'},
            {'tag': 'tag_2',
             'name': 'prob_2'},
        ])

        tag_getter = TagGetter(db_gateway=Mock(), presenter=Mock())
        res = tag_getter._get_problems_per_tag()

        assert_frame_equal(expected_df, res)

    @patch.object(ProblemGetter, 'get_prioritized_problems')
    def test_get_problems_per_tag_no_data(self, mock_get_prioritized_problems):
        mock_get_prioritized_problems.return_value = pd.DataFrame(columns=[
            'difficulty', 'name', 'tags', 'url', 'problem_id', 'ts_logged',
            'result', 'ease', 'interval', 'RF', 'KS'])

        expected_df = pd.DataFrame(columns=[
            'difficulty', 'name', 'tag', 'url', 'problem_id', 'ts_logged',
            'result', 'ease', 'interval', 'RF', 'KS'])

        tag_getter = TagGetter(db_gateway=Mock(), presenter=Mock())
        res = tag_getter._get_problems_per_tag()

        assert_frame_equal(expected_df, res,
                           check_index_type=False)
