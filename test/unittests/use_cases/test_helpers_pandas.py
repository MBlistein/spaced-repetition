
import unittest

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from spaced_repetition.use_cases.helpers_pandas import add_missing_columns


class TestAddMissingColumns(unittest.TestCase):
    def test_add_missing_columns(self):
        input_df = pd.DataFrame(data={'a': [1, 2, 3]})

        expected_res = input_df.copy()
        expected_res['some_col'] = pd.Series(dtype=np.float)
        expected_res['difficulty'] = pd.Series(dtype='object')
        expected_res['interval'] = pd.Series(dtype='int32')
        expected_res['last_access'] = pd.Series(dtype='datetime64[ns]')

        res = add_missing_columns(input_df,
                                  required_columns=['some_col',
                                                    'difficulty',
                                                    'interval',
                                                    'last_access'])

        assert_frame_equal(expected_res, res)
