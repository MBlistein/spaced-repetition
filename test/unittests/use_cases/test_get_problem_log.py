import datetime as dt
import unittest
from unittest.mock import Mock, patch

import pandas as pd
from dateutil.tz import gettz
from pandas.testing import assert_frame_equal

from spaced_repetition.domain.problem_log import (DEFAULT_EASE, INTERVAL_NON_OPTIMAL_SOLUTION,
                                                  ProblemLogCreator, Result)
from spaced_repetition.domain.score import Score
from spaced_repetition.use_cases.get_problem_log import ProblemLogGetter
from spaced_repetition.use_cases.helpers_pandas import add_missing_columns


class TestProblemLogGetter(unittest.TestCase):
    def setUp(self):
        self.time_1 = dt.datetime(2021, 1, 10, 1)
        self.time_2 = dt.datetime(2021, 1, 10, 5)

        self.problem_log_1 = ProblemLogCreator.create(
            last_log=None,
            problem_id=1,
            result=Result.NO_IDEA,
            timestamp=self.time_1)

        problem_logs = [
            self.problem_log_1,
            ProblemLogCreator.create(
                last_log=None,
                problem_id=2,
                result=Result.SOLVED_OPTIMALLY_WITH_HINT,
                timestamp=self.time_2)]

        self.plg = ProblemLogGetter(db_gateway=Mock(), presenter=Mock())
        self.plg.repo.get_problem_logs.return_value = problem_logs

    def test_get_problem_logs(self):
        expected_res = pd.DataFrame([
            {'ease': DEFAULT_EASE,
             'interval': INTERVAL_NON_OPTIMAL_SOLUTION,
             'problem_id': 1,
             'result': Result.NO_IDEA,
             'ts_logged': self.time_1},
            {'ease': DEFAULT_EASE,
             'interval': INTERVAL_NON_OPTIMAL_SOLUTION,
             'problem_id': 2,
             'result': Result.SOLVED_OPTIMALLY_WITH_HINT,
             'ts_logged': self.time_2}])

        assert_frame_equal(self.plg._get_problem_logs(problem_ids=[1, 2]),
                           expected_res)

    def test_get_problem_logs_no_problems(self):
        plg = ProblemLogGetter(db_gateway=Mock(), presenter=Mock())
        plg.repo.get_problem_logs.return_value = []

        assert_frame_equal(plg._get_problem_logs(),
                           pd.DataFrame())

    def test_get_problem_logs_for_specific_problems(self):
        self.plg._get_problem_logs(problem_ids=[1])

        # noinspection PyUnresolvedReferences
        self.plg.repo.get_problem_logs.assert_called_once_with(
            problem_ids=[1])

    def test_log_to_row_content(self):
        expected_res = {
            'ease': DEFAULT_EASE,
            'interval': INTERVAL_NON_OPTIMAL_SOLUTION,
            'problem_id': 1,
            'result': Result.NO_IDEA,
            'ts_logged': self.time_1}

        self.assertEqual(
            ProblemLogGetter._log_to_row_content(p_log=self.problem_log_1),
            expected_res)

    @patch.object(ProblemLogGetter, '_last_log_per_problem')
    @patch.object(ProblemLogGetter, '_get_problem_logs')
    def test_get_last_log_per_problem(self, mock_get_problem_logs,
                                      mock_last_log_per_problem):
        mock_get_problem_logs.return_value = 'dummy_return'

        self.plg._get_last_log_per_problem(problem_ids=[1, 2, 3])

        mock_get_problem_logs.assert_called_once_with(problem_ids=[1, 2, 3])
        mock_last_log_per_problem.assert_called_once_with('dummy_return')

    def test_last_log_per_problem(self):
        p1_log_data = {'ease': 2.5,
                       'interval': 10,
                       'problem_id': 1,
                       'result': Result.SOLVED_OPTIMALLY_IN_UNDER_25,
                       'ts_logged': dt.datetime(2021, 1, 1, 8),
                       'other_col': 'some_val'}
        p1_log_data_2 = p1_log_data.copy()
        p1_log_data_2['ts_logged'] = dt.datetime(2021, 1, 1, 9)

        p2_log_data = p1_log_data.copy()
        p2_log_data['problem_id'] = 2
        p2_log_data['ts_logged'] = dt.datetime(2021, 1, 1, 15)

        p2_log_data_2 = p2_log_data.copy()
        p2_log_data_2['ts_logged'] = dt.datetime(2021, 1, 1, 7)

        log_df = pd.DataFrame(data=[p1_log_data, p1_log_data_2,
                                    p2_log_data, p2_log_data_2])

        expected_df = pd.DataFrame(data=[
            {'ease': 2.5,
             'interval': 10,
             'problem_id': 1,
             'result': Result.SOLVED_OPTIMALLY_IN_UNDER_25,
             'ts_logged': dt.datetime(2021, 1, 1, 9)},
            {'ease': 2.5,
             'interval': 10,
             'problem_id': 2,
             'result': Result.SOLVED_OPTIMALLY_IN_UNDER_25,
             'ts_logged': dt.datetime(2021, 1, 1, 15)}])

        res = ProblemLogGetter._last_log_per_problem(log_df=log_df)

        # drop numeric index, which depends on the order of log_df entries
        res.reset_index(drop=True, inplace=True)

        assert_frame_equal(expected_df, res,
                           check_like=True)

    def test_last_log_per_problem_no_data(self):
        columns = ['problem_id', 'ts_logged', 'result', 'ease', 'interval']
        expected_df = add_missing_columns(df=pd.DataFrame(),
                                          required_columns=columns)

        assert_frame_equal(
            expected_df,
            ProblemLogGetter._last_log_per_problem(log_df=pd.DataFrame()))

    def test_add_scores(self):
        log_df = pd.DataFrame(data=[
            {'problem_id': 1,
             'result': Result.SOLVED_OPTIMALLY_SLOWER.value}
        ])

        expected_df = pd.DataFrame(data=[
            {'problem_id': 1,
             'result': Result.SOLVED_OPTIMALLY_SLOWER.value,
             'score': Score.MEDIUM.value}
        ])

        assert_frame_equal(ProblemLogGetter._add_scores(log_df=log_df),
                           expected_df)

    @patch.object(ProblemLogGetter, '_get_knowledge_scores')
    @patch.object(ProblemLogGetter, '_get_last_log_per_problem')
    def test_get_problem_knowledge_scores(self, mock_get_last_log_per_problem,
                                          mock_get_knowledge_scores):
        mock_get_last_log_per_problem.return_value = 'dummy_return'

        self.plg.get_problem_knowledge_scores(problem_ids=[1, 2])

        mock_get_last_log_per_problem.assert_called_once_with(problem_ids=[1, 2])
        mock_get_knowledge_scores.assert_called_once_with(log_data='dummy_return')

    def test_retention_score(self):
        interval = 5
        ts_logged = dt.datetime(2021, 1, 1, tzinfo=gettz('UTC'))
        df_row = pd.Series(data={'interval': interval,
                                 'ts_logged': pd.Timestamp(ts_logged)})

        params = [
            (dt.timedelta(days=-interval), 1.0),
            (dt.timedelta(days=interval), 1.0),
            (dt.timedelta(days=2 * interval), 0.5),
            (dt.timedelta(days=3 * interval), 0.25),
        ]

        for days_late, expected_rf in params:
            with self.subTest(days_late=days_late, expected_rf=expected_rf):
                ts = ts_logged + days_late

                self.assertAlmostEqual(
                    expected_rf,
                    ProblemLogGetter._retention_score(df_row=df_row, ts=ts))

    def test_get_knowledge_scores(self):
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

        res = ProblemLogGetter._get_knowledge_scores(log_data=last_log_data,
                                                     ts=ts)

        assert_frame_equal(expected_df.reindex(columns=cols_in_order),
                           res.reindex(columns=cols_in_order))

    def test_get_knowledge_scores_empty_input(self):
        columns_log_data = ['problem_id', 'ts_logged', 'result', 'ease',
                            'interval']
        last_log_data = add_missing_columns(df=pd.DataFrame(),
                                            required_columns=columns_log_data)

        columns_knowledge_df = columns_log_data + ['RF', 'KS']
        expected_df = add_missing_columns(df=pd.DataFrame(),
                                          required_columns=columns_knowledge_df)

        res = ProblemLogGetter._get_knowledge_scores(log_data=last_log_data)

        assert_frame_equal(expected_df, res, check_like=True)
