import unittest
from unittest.mock import patch, Mock

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

        expected_df = pd.DataFrame(data={'name': ['tag_1', 'tag_2'],
                                         'tag_id': [None, None]})

        tag_df = tag_getter.get_tags()

        assert_frame_equal(expected_df, tag_df)

    def test_get_tags_no_data(self):
        tag_getter = TagGetter(db_gateway=Mock(), presenter=Mock())
        tag_getter.repo.get_tags.return_value = []

        tag_df = tag_getter.get_tags()

        self.assertTrue(tag_df.empty)
        self.assertEqual(['name', 'tag_id'], tag_df.columns.to_list())


class TestGetPrioritizedTags(unittest.TestCase):
    def setUp(self) -> None:
        self.prob_data_easy_1 = {
            'name': 'easy_problem_1',
            'difficulty': Difficulty.EASY,
            'KS': 3,
            'tags': 'tag_1'}

        self.prob_data_easy_2 = {
            'name': 'easy_problem_2',
            'difficulty': Difficulty.EASY,
            'KS': 5,
            'tags': 'tag_1'}

        self.prob_data_medium = {
            'name': 'medium_problem',
            'difficulty': Difficulty.MEDIUM,
            'KS': 2,
            'tags': 'tag_1'}
        self.prob_data_tag_2_easy = {
            'name': 'easy_problem_3',
            'difficulty': Difficulty.EASY,
            'KS': 5,
            'tags': 'tag_2'}

        self.prob_data_tag_2_medium = {
            'name': 'medium_problem_2',
            'difficulty': Difficulty.MEDIUM,
            'KS': 4,
            'tags': 'tag_2'}

        self.prob_data_tag_2_hard = {
            'name': 'medium_problem_2',
            'difficulty': Difficulty.HARD,
            'KS': 3,
            'tags': 'tag_2'}

        self.empty_problem_df = pd.DataFrame(columns=[
            'difficulty', 'name', 'tags', 'url', 'problem_id', 'ts_logged',
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
            self.prob_data_tag_2_hard])

        expected_res = pd.DataFrame(data=[
            {'tags': 'tag_1',
             'KS (weighted avg)': 2.0,
             'experience': 0.6,
             'num_problems': 3,
             'priority': 1.2},
            {'tags': 'tag_2',
             'KS (weighted avg)': 4.0,
             'experience': 0.6,
             'num_problems': 3,
             'priority': 2.4}
        ])

        res = TagGetter._prioritize_tags(problem_data=test_df)

        assert_frame_equal(expected_res,
                           res.reindex(columns=expected_res.columns))

    def test_prioritize_tags_empty_data(self):
        res = TagGetter._prioritize_tags(problem_data=self.empty_problem_df)

        assert_frame_equal(self.empty_tag_df, res)

    @patch.object(ProblemGetter, 'get_prioritized_problems')
    @patch.object(TagGetter, '_prioritize_tags')
    def test_get_prioritized_tags(self, mock_prioritize_tags,
                                  mock_get_prio_problems):
        mock_prioritize_tags.return_value = 'correct'
        fake_problem_data = pd.DataFrame(data=[{'row': 'non-empty content'}])
        mock_get_prio_problems.return_value = fake_problem_data
        tag_getter = TagGetter(db_gateway=Mock(), presenter=Mock())
        tag_getter.repo.get_tags.return_value = [TagCreator.create('tag_1'),
                                                 TagCreator.create('tag_2')]

        res = tag_getter.get_prioritized_tags(sub_str='test_str')

        tag_getter.repo.get_tags.assert_called_once_with(sub_str='test_str')  # noqa
        mock_get_prio_problems.assert_called_once_with(
            tags_any=['tag_1', 'tag_2'])
        mock_prioritize_tags.assert_called_once_with(
            problem_data=fake_problem_data)
        self.assertEqual('correct', res)

    @patch.object(ProblemGetter, 'get_prioritized_problems')
    def test_get_prioritized_tags_no_data(self, mock_get_prioritized_problems):
        mock_get_prioritized_problems.return_value = self.empty_problem_df

        tag_getter = TagGetter(db_gateway=Mock(), presenter=Mock())
        tag_getter.repo.get_tags.return_value = []

        res = tag_getter.get_prioritized_tags()

        tag_getter.repo.get_tags.assert_called_once_with(sub_str=None)  # noqa
        mock_get_prioritized_problems.assert_called_once_with(tags_any=None)
        assert_frame_equal(self.empty_tag_df, res)
