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
from spaced_repetition.use_cases.helpers_pandas import add_missing_columns


class TestGetTags(unittest.TestCase):
    def setUp(self) -> None:
        self.tag_1 = TagCreator.create(name='tag_1')
        self.tag_2 = TagCreator.create(name='tag_2')

    def test_get_tags(self):

        tag_getter = TagGetter(db_gateway=Mock(), presenter=Mock())
        tag_getter.repo.get_tags.return_value = [self.tag_1, self.tag_2]

        expected_df = pd.DataFrame(data={'tag': ['tag_1', 'tag_2'],
                                         'tag_id': [None, None]})

        tag_df = tag_getter._get_tags()

        assert_frame_equal(expected_df, tag_df)

    def test_get_tags_no_data(self):
        tag_getter = TagGetter(db_gateway=Mock(), presenter=Mock())
        tag_getter.repo.get_tags.return_value = []

        tag_df = tag_getter._get_tags()

        self.assertTrue(tag_df.empty)
        self.assertEqual(['tag', 'tag_id'], tag_df.columns.to_list())

    def test_get_existing_tags(self):
        repo = Mock()
        repo.get_tags.return_value = [self.tag_1]
        tag_getter = TagGetter(db_gateway=repo, presenter=Mock())

        tags = tag_getter.get_existing_tags(names=[self.tag_1.name])

        self.assertEqual(tags, [self.tag_1])

    def test_get_existing_tags_raises_missing(self):
        repo = Mock()
        repo.get_tags.return_value = [self.tag_1]
        tag_getter = TagGetter(db_gateway=repo, presenter=Mock())

        with self.assertRaises(ValueError) as context:
            tag_getter.get_existing_tags(names=[self.tag_1.name,
                                                self.tag_2.name])

        self.assertEqual(str(context.exception),
                         "The following tag names don't exist: {'tag_2'}")


class TestGetPrioritizedTags(unittest.TestCase):
    def setUp(self) -> None:
        self.data_tag1_prob1_easy = {
            'problem': 'easy_problem_1',
            'difficulty': Difficulty.EASY,
            'KS': 3,
            'tag': 'tag_1',
            'ts_logged': dt.datetime(2021, 1, 1, 10)}

        self.data_tag1_prob2_easy = {
            'problem': 'easy_problem_2',
            'difficulty': Difficulty.EASY,
            'KS': 5,
            'tag': 'tag_1',
            'ts_logged': dt.datetime(2021, 1, 1, 10)}

        self.data_tag1_prob3_medium = {
            'problem': 'medium_problem',
            'difficulty': Difficulty.MEDIUM,
            'KS': 2,
            'tag': 'tag_1',
            'ts_logged': dt.datetime(2021, 1, 1, 10)}

        self.data_tag2_prob4_easy = {
            'problem': 'easy_problem_3',
            'difficulty': Difficulty.EASY,
            'KS': 5,
            'tag': 'tag_2',
            'ts_logged': dt.datetime(2021, 1, 1, 10)}

        self.data_tag2_prob5_medium = {
            'problem': 'medium_problem_2',
            'difficulty': Difficulty.MEDIUM,
            'KS': 4,
            'tag': 'tag_2',
            'ts_logged': dt.datetime(2021, 1, 1, 10)}

        self.data_tag2_prob6_hard = {
            'problem': 'medium_problem_2',
            'difficulty': Difficulty.HARD,
            'KS': 3,
            'tag': 'tag_2',
            'ts_logged': dt.datetime(2021, 1, 1, 10)}

        self.data_tag_untried_problem = {
            'problem': 'untried_problem',
            'difficulty': Difficulty.HARD,
            'KS': np.nan,
            'tag': 'tag_with_untried_problem',
            'ts_logged': np.nan}

        self.data_tag_no_problems = {
            'problem': np.nan,
            'difficulty': np.nan,
            'KS': np.nan,
            'tag': 'tag_wo_problems',
            'ts_logged': np.nan}

        self.empty_problem_df = add_missing_columns(
            df=pd.DataFrame(),
            required_columns=['difficulty', 'problem', 'tag', 'url', 'problem_id',
                              'ts_logged', 'result', 'ease', 'interval', 'RF',
                              'KS'])

        self.empty_tag_df = add_missing_columns(
            df=pd.DataFrame(),
            required_columns=['tags', 'experience', 'KW (weighted avg)',
                              'num_problems', 'priority'])

    def test_prioritize(self):
        test_df = pd.DataFrame(data=[
            self.data_tag1_prob1_easy,
            self.data_tag1_prob2_easy,
            self.data_tag1_prob3_medium])

        expected_res = pd.Series(
            data={
                'KS (weighted avg)': 2,  # max(0.5 * 4, 0.75 * 2)
                'experience': 0.6,
                'num_problems': 3,
                'priority': 1.2},
            dtype='object')

        res = TagGetter._prioritize(group_df=test_df)

        assert_series_equal(expected_res,
                            res.reindex(index=expected_res.index))

    def test_prioritize_tag_without_problem(self):
        test_df = pd.DataFrame(data=[
            self.data_tag_no_problems])

        expected_res = pd.Series(
            data={
                'KS (weighted avg)': 0.0,
                'experience': 0.0,
                'num_problems': 0,
                'priority': 0.0},
            dtype='object')

        res = TagGetter._prioritize(group_df=test_df)

        assert_series_equal(expected_res,
                            res.reindex(index=expected_res.index))

    def test_prioritize_tags(self):
        test_df = pd.DataFrame(data=[
            self.data_tag1_prob1_easy,
            self.data_tag1_prob2_easy,
            self.data_tag1_prob3_medium,
            self.data_tag2_prob4_easy,
            self.data_tag2_prob5_medium,
            self.data_tag2_prob6_hard,
            self.data_tag_untried_problem,
            self.data_tag_no_problems])

        expected_res = pd.DataFrame(data=[
            {'tag': 'tag_1',
             'KS (weighted avg)': 2.0,
             'experience': 0.6,
             'num_problems': 3,
             'priority': 1.2},
            {'tag': 'tag_2',
             'KS (weighted avg)': 3.0,    # max(0.5 * 5 = 2.5, 0.75 * 4 = 3, 3)
             'experience': 0.6,
             'num_problems': 3,
             'priority': 1.8},
            {'tag': 'tag_with_untried_problem',
             'KS (weighted avg)': 0.0,
             'experience': 0.0,
             'num_problems': 1,
             'priority': 0.0},
            {'tag': 'tag_wo_problems',
             'KS (weighted avg)': 0.0,
             'experience': 0.0,
             'num_problems': 0,
             'priority': 0.0}
        ])

        res = TagGetter._prioritize_tags(tag_data=test_df)

        assert_frame_equal(expected_res, res,
                           check_like=True)

    def test_prioritize_tags_empty_data(self):
        res = TagGetter._prioritize_tags(tag_data=self.empty_problem_df)

        assert_frame_equal(self.empty_tag_df, res, check_like=True)

    def test_merge_tag_and_knowledge_data(self):
        tag_df = pd.DataFrame({'tag': ['tag_1', 'tag_2'],
                               'tag_id': [1, 2]})
        knowledge_df = pd.DataFrame({'tag': ['tag_1', 'tag_2', 'tag_2'],
                                     'KS': [55, 1, 44],
                                     'problem': ['prob1', 'prob2', 'prob3']})
        expected_res = pd.DataFrame({'tag': ['tag_1', 'tag_2', 'tag_2'],
                                     'tag_id': [1, 2, 2],
                                     'KS': [55, 1, 44],
                                     'problem': ['prob1', 'prob2', 'prob3']})

        res = TagGetter._merge_tag_and_knowledge_data(tag_df, knowledge_df)

        assert_frame_equal(expected_res, res)

    def test_merge_tag_and_knowledge_data_filter_tags(self):
        tag_df = pd.DataFrame({'tag': ['tag_1'],
                               'tag_id': [1]})
        knowledge_df = pd.DataFrame({'tag': ['tag_1', 'tag_2'],
                                     'KS': [55, 44]})
        expected_res = pd.DataFrame({'tag': ['tag_1'],
                                     'tag_id': [1],
                                     'KS': [55]})

        res = TagGetter._merge_tag_and_knowledge_data(tag_df, knowledge_df)

        assert_frame_equal(expected_res, res)

    def test_merge_tag_and_knowledge_data_unlogged_tag(self):
        tag_df = pd.DataFrame({'tag': ['tag_1', 'unlogged_tag'],
                               'tag_id': [1, 2]})
        knowledge_df = pd.DataFrame({'tag': ['tag_1'],
                                     'KS': [55]})
        expected_res = pd.DataFrame({'tag': ['tag_1', 'unlogged_tag'],
                                     'tag_id': [1, 2],
                                     'KS': [55, np.nan]})

        res = TagGetter._merge_tag_and_knowledge_data(tag_df, knowledge_df)

        assert_frame_equal(expected_res, res)

    @patch.object(TagGetter, '_get_tags')
    @patch.object(ProblemGetter, 'get_knowledge_status')
    def test_get_prioritized_tags_no_data(
            self, mock_get_knowledge_status, mock_get_tags):
        # prepare
        mock_get_knowledge_status.return_value = self.empty_problem_df
        mock_get_tags.return_value = add_missing_columns(
            df=pd.DataFrame(), required_columns=['tag', 'tag_id'])

        tag_getter = TagGetter(db_gateway=Mock(), presenter=Mock())

        # call
        res = tag_getter._get_prioritized_tags()

        # assert
        mock_get_tags.assert_called_once_with(sub_str=None)
        mock_get_knowledge_status.assert_called_once_with()
        assert_frame_equal(self.empty_tag_df, res, check_like=True)

    def test_mean_knowledge_score(self):
        data_df = pd.DataFrame(data=[
            {'difficulty': Difficulty.EASY, 'KS': 3},
            {'difficulty': Difficulty.EASY, 'KS': 1},
            {'difficulty': Difficulty.EASY, 'KS': np.nan}
        ])

        res = TagGetter._mean_knowledge_score(df=data_df,
                                              difficulty=Difficulty.EASY)

        self.assertAlmostEqual(2.0, res)
