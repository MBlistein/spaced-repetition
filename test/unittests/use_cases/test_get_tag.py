import datetime as dt
import unittest
from unittest.mock import Mock, patch

import pandas as pd
from dateutil.tz import gettz
from pandas.testing import assert_frame_equal

from spaced_repetition.domain.tag import Tag
from spaced_repetition.domain.score import Score
from spaced_repetition.use_cases.get_problem import ProblemGetter


# class TestGetTagDF(unittest.TestCase):
#     def setUp(self):
#         mock_gateway = Mock()
#         mock_gateway.get_tags.return_value = [Tag(name='test_tag',
#                                                   tag_id=1)]
#
#         self.p_g = ProblemGetter(db_gateway=mock_gateway, presenter=Mock())
#
#     @patch.object(ProblemGetter, attribute='get_problem_df')
#     def test_get_task_df_no_problems_found(self, mock_get_problem_df):
#         mock_get_problem_df.return_value = pd.DataFrame()
#         expected_df = pd.DataFrame()
#
#         assert_frame_equal(self.p_g.get_tag_df(),
#                            expected_df)
#
#     @patch.object(ProblemGetter, attribute='get_problem_df')
#     def test_get_tag_df(self, mock_get_problem_df):
#         mock_get_problem_df.return_value = pd.DataFrame(data=[
#             {'name': 'testname',
#              'problem_id': 3,
#              'difficulty': 'EASY',
#              'tags': 'test-tag',
#              'url': 'test-url',
#              'ts_logged': dt.datetime(2021, 1, 5, 10),
#              'score': Score.BAD.value}
#         ])
#
#         self.p_g.get_tag_df()
#
#     @patch.object(ProblemGetter, attribute='get_problem_df')
#     def test_get_tag_df(self, mock_get_problem_df):
#         mock_get_problem_df.return_value = pd.DataFrame(data=[
#             {'name': 'test_problem_1',
#              'problem_id': 1,
#              'difficulty': 'EASY',
#              'tags': 'test_tag',
#              'ts_logged': dt.datetime(2021, 1, 5, 10, tzinfo=gettz('UTC')),
#              'score': Score.VERY_GOOD.value},
#             {'name': 'test_problem_2',
#              'problem_id': 2,
#              'difficulty': 'EASY',
#              'tags': 'test_tag',
#              'ts_logged': dt.datetime(2021, 1, 5, 12, tzinfo=gettz('UTC')),
#              'score': Score.MEDIUM.value},
#         ])
#
#         expected_df = pd.DataFrame(data=[
#             {'tags': 'test_tag',
#              'prio': 1,
#              'avg_score': float(Score.GOOD.value),
#              'last_access': dt.datetime(2021, 1, 5, 12, tzinfo=gettz('UTC')),
#              'num_problems': 2}
#         ]).set_index('prio')
#         p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())
#
#         assert_frame_equal(p_g.get_tag_df(),
#                            expected_df)
