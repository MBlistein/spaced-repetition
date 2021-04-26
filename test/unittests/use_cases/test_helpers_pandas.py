
import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from spaced_repetition.domain.problem import Difficulty
from spaced_repetition.use_cases.helpers_pandas import (add_missing_columns,
                                                        denormalize_tags)


class TestAddMissingColumns(unittest.TestCase):
    def test_add_missing_columns(self):
        input_df = pd.DataFrame(data={'a': [1, 2, 3]})

        expected_res = input_df.copy()
        expected_res['some_col'] = pd.Series(dtype=float)
        expected_res['difficulty'] = pd.Series(dtype='object')
        expected_res['interval'] = pd.Series(dtype='int32')
        expected_res['last_access'] = pd.Series(dtype='datetime64[ns]')

        res = add_missing_columns(input_df,
                                  required_columns=['some_col',
                                                    'difficulty',
                                                    'interval',
                                                    'last_access'])

        assert_frame_equal(expected_res, res)

    def test_denormalize_tags(self):
        problem_df = pd.DataFrame(data=[{
            'difficulty': Difficulty.EASY,
            'problem': 'test_problem',
            'problem_id': 1,
            'tags': 'tag_1, tag_2',
            'url': 'some_url.com'}])

        expected_res = pd.DataFrame(data={
            'difficulty': [Difficulty.EASY] * 2,
            'problem': ['test_problem'] * 2,
            'problem_id': [1] * 2,
            'tag': ['tag_1', 'tag_2'],
            'url': ['some_url.com'] * 2})

        res = denormalize_tags(problem_df)

        assert_frame_equal(expected_res, res)

    def test_denormalize_tags_empty_input(self):
        expected_res = pd.DataFrame()

        res = denormalize_tags(pd.DataFrame())

        assert_frame_equal(expected_res, res)
