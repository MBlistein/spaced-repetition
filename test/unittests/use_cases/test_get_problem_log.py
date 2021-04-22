import datetime as dt
import unittest
from unittest.mock import Mock, patch

import pandas as pd
from dateutil.tz import gettz
from pandas.testing import assert_frame_equal

from spaced_repetition.domain.problem_log import (
    DEFAULT_EASE,
    INTERVAL_NON_OPTIMAL_SOLUTION,
    ProblemLogCreator,
    Result)
from spaced_repetition.use_cases.get_problem_log import ProblemLogGetter
from spaced_repetition.use_cases.helpers_pandas import add_missing_columns
from spaced_repetition.domain.tag import TagCreator


class TestProblemLogGetter(unittest.TestCase):
    def setUp(self):
        self.time_1 = dt.datetime(2021, 1, 10, 1)
        self.time_2 = dt.datetime(2021, 1, 10, 5)

        self.tag_1 = TagCreator.create('tag_1')
        self.tag_2 = TagCreator.create('tag_2')

        self.problem_log_1 = ProblemLogCreator.create(
            comment='problem_log_1 comment',
            last_log=None,
            problem_id=1,
            result=Result.NO_IDEA,
            tags=[self.tag_1, self.tag_2],
            timestamp=self.time_1)

        problem_logs = [
            self.problem_log_1,
            ProblemLogCreator.create(
                last_log=None,
                problem_id=2,
                result=Result.SOLVED_OPTIMALLY_WITH_HINT,
                tags=[self.tag_2],
                timestamp=self.time_2)]

        self.plg = ProblemLogGetter(db_gateway=Mock(), presenter=Mock())
        self.plg.repo.get_problem_logs.return_value = problem_logs

    def test_get_problem_logs(self):
        expected_res = pd.DataFrame([
            {'comment': 'problem_log_1 comment',
             'ease': DEFAULT_EASE,
             'interval': INTERVAL_NON_OPTIMAL_SOLUTION,
             'problem_id': 1,
             'result': Result.NO_IDEA,
             'tags': 'tag_1, tag_2',
             'ts_logged': self.time_1},
            {'comment': '',
             'ease': DEFAULT_EASE,
             'interval': INTERVAL_NON_OPTIMAL_SOLUTION,
             'problem_id': 2,
             'result': Result.SOLVED_OPTIMALLY_WITH_HINT,
             'tags': 'tag_2',
             'ts_logged': self.time_2}])

        assert_frame_equal(self.plg.get_problem_logs(problem_ids=[1, 2]),
                           expected_res, check_like=True)

    def test_log_to_row_content(self):
        expected_res = {
            'comment': 'problem_log_1 comment',
            'ease': DEFAULT_EASE,
            'interval': INTERVAL_NON_OPTIMAL_SOLUTION,
            'problem_id': 1,
            'result': Result.NO_IDEA,
            'tags': 'tag_1, tag_2',
            'ts_logged': self.time_1}

        self.assertEqual(
            ProblemLogGetter._log_to_row(p_log=self.problem_log_1),
            expected_res)

    def test_retention_score(self):
        interval = 5
        ts_logged = dt.datetime(2021, 1, 1, tzinfo=gettz('UTC'))
        df_row = pd.Series(data={'interval': interval,
                                 'ts_logged': pd.Timestamp(ts_logged)})

        params = [
            (dt.timedelta(days=-interval), 1.0),
            (dt.timedelta(days=interval), 1.0),
            (dt.timedelta(days=interval, hours=1), 0.994240423818),
            (dt.timedelta(days=2 * interval), 0.5),
            (dt.timedelta(days=3 * interval), 0.25),
        ]

        for delta_t, expected_rf in params:
            with self.subTest(time_passed=delta_t, expected_rf=expected_rf):
                ts = ts_logged + delta_t

                self.assertAlmostEqual(
                    expected_rf,
                    ProblemLogGetter._retention_score(df_row=df_row, ts=ts))

    def test_add_knowledge_scores(self):
        last_log_data = pd.DataFrame(data=[
            {'problem_id': 1,
             'ts_logged': dt.datetime(2021, 1, 1, tzinfo=gettz('UTC')),
             'result': Result.SOLVED_OPTIMALLY_IN_UNDER_25,
             'interval': 10,
             'ease': 2}
        ])
        ts = dt.datetime(2021, 1, 21, tzinfo=gettz('UTC'))

        expected_df = last_log_data.copy()
        expected_df['RF'] = pd.Series(data=[0.5])
        expected_df['KS'] = pd.Series(data=[2.0])

        cols_in_order = sorted(expected_df.columns)

        res = ProblemLogGetter._add_knowledge_scores(log_data=last_log_data,
                                                     ts=ts)

        assert_frame_equal(expected_df.reindex(columns=cols_in_order),
                           res.reindex(columns=cols_in_order))

    def test_add_knowledge_scores_empty_input(self):
        columns_log_data = ['problem_id', 'ts_logged', 'result', 'ease',
                            'interval']
        last_log_data = add_missing_columns(df=pd.DataFrame(),
                                            required_columns=columns_log_data)

        columns_knowledge_df = columns_log_data + ['RF', 'KS']
        expected_df = add_missing_columns(df=pd.DataFrame(),
                                          required_columns=columns_knowledge_df)

        res = ProblemLogGetter._add_knowledge_scores(log_data=last_log_data)

        assert_frame_equal(expected_df, res, check_like=True)


class TestGetKnowledgeStatus(unittest.TestCase):
    def setUp(self):
        self.time_1 = dt.datetime(2021, 1, 10, 1)
        self.time_2 = dt.datetime(2021, 1, 10, 5)

        self.tag_1 = TagCreator.create('tag_1')
        self.tag_2 = TagCreator.create('tag_2')

        self.problem_log_1 = ProblemLogCreator.create(
            comment='problem_log_1 comment',
            ease=1,
            interval=2,
            last_log=None,
            problem_id=1,
            result=Result.NO_IDEA,
            tags=[self.tag_1, self.tag_2],
            timestamp=self.time_1)

        self.problem_log_2 = ProblemLogCreator.create(
            ease=3,
            interval=4,
            last_log=None,
            problem_id=1,
            result=Result.SOLVED_OPTIMALLY_WITH_HINT,
            tags=[self.tag_2],
            timestamp=self.time_2)

        self.plg = ProblemLogGetter(db_gateway=Mock(), presenter=Mock())
        self.plg.repo.get_problem_logs.return_value = [self.problem_log_1,
                                                       self.problem_log_2]

        self.prob1_tag1_ts1_data = {
            'comment': 'problem_log_1 comment',
            'ease': 1,
            'interval': 2,
            'problem_id': 1,
            'result': Result.NO_IDEA,
            'tag': 'tag_1',
            'ts_logged': self.time_1}
        self.prob1_tag2_ts1_data = {
             'comment': 'problem_log_1 comment',
             'ease': 1,
             'interval': 2,
             'problem_id': 1,
             'result': Result.NO_IDEA,
             'tag': 'tag_2',
             'ts_logged': self.time_1}
        self.prob1_tag2_ts2_data = {
              'comment': '',
              'ease': 3,
              'interval': 4,
              'problem_id': 1,
              'result': Result.SOLVED_OPTIMALLY_WITH_HINT,
              'tag': 'tag_2',
              'ts_logged': self.time_2}

    def test_denormalize_logs(self):
        expected_result = [self.prob1_tag1_ts1_data,
                           self.prob1_tag2_ts1_data,
                           self.prob1_tag2_ts2_data]

        res = self.plg._denormalize_logs(p_logs=[self.problem_log_1,
                                                 self.problem_log_2])

        self.assertEqual(expected_result, res)

    def test_get_problem_log_data(self):
        expected_result = pd.DataFrame(data=[self.prob1_tag1_ts1_data,
                                             self.prob1_tag2_ts1_data,
                                             self.prob1_tag2_ts2_data])

        res = self.plg._get_problem_log_data()

        assert_frame_equal(expected_result, res)

    def test_last_entry_per_problem_tag_combo(self):
        input_df = pd.DataFrame(data=[self.prob1_tag1_ts1_data,
                                      self.prob1_tag2_ts1_data,
                                      self.prob1_tag2_ts2_data])
        expected_result = pd \
            .DataFrame(data=[self.prob1_tag1_ts1_data,
                             self.prob1_tag2_ts2_data]) \
            .loc[:, ['problem_id', 'tag', 'ts_logged', 'result', 'ease',
                     'interval']]

        res = self.plg._last_entry_per_problem_tag_combo(input_df) \
            .reset_index(drop=True)  # filtered rows make index non-continuous

        assert_frame_equal(expected_result, res)

    def test_last_entry_per_problem_tag_combo_no_data(self):
        columns = ['problem_id', 'tag', 'ts_logged', 'result', 'ease',
                   'interval']
        expected_result = add_missing_columns(df=pd.DataFrame(),
                                              required_columns=columns)
        input_df = pd.DataFrame(pd.DataFrame())

        res = self.plg._last_entry_per_problem_tag_combo(input_df)

        assert_frame_equal(expected_result,
                           res)  # empty df has range index

    @patch.object(ProblemLogGetter, '_add_knowledge_scores')
    @patch.object(ProblemLogGetter, '_last_entry_per_problem_tag_combo')
    @patch.object(ProblemLogGetter, '_get_problem_log_data')
    def test_get_knowledge_status(self, mock_get_problem_log_data,
                                  mock_get_last_entry,
                                  mock_add_knowledge_scores):
        mock_get_problem_log_data.return_value = 'log_data'
        mock_get_last_entry.return_value = 'last_entries'

        self.plg.get_knowledge_status()

        mock_get_problem_log_data.assert_called_once()
        mock_get_last_entry.assert_called_once_with(plog_df='log_data')
        mock_add_knowledge_scores.assert_called_once_with(log_data='last_entries')
