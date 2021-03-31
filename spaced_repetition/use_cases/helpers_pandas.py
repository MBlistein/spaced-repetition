"""Time serialization"""

from typing import List

import numpy as np
import pandas as pd


TYPE_MAPPER = {
    'difficulty': 'object',
    'interval': 'int32',
    'last_access': 'datetime64[ns]',
    'last_result': 'object',
    'num_problems': 'int32',
    'problem_id': 'int32',
    'tag': 'object',
    'tags': 'object',
    'tag_id': 'int32',
    'url': 'object',
}


def add_missing_columns(df, required_columns: List[str]):
    """ Adds missing columns of expected type """
    df = df.copy()
    for col in required_columns:
        if col not in df.columns:
            df[col] = pd.Series(dtype=TYPE_MAPPER.get(col, np.float))
    return df
