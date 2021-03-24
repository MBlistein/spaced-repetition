import datetime as dt
import unittest
from unittest.mock import patch

from dateutil.tz import gettz

from spaced_repetition.domain.problem_log import (DEFAULT_EASE, DEFAULT_INTERVAL,
                                                  ProblemLog, ProblemLogCreator,
                                                  Result)


class TestProblemLogCreator(unittest.TestCase):
    @patch.object(ProblemLogCreator, 'calc_ease')
    @patch.object(ProblemLogCreator, 'calc_interval')
    def test_create_spacing_calc_calls(self, mock_calc_int, mock_calc_ease):
        params = [
            (2.3, 17, [mock_calc_int.assert_not_called,
                       mock_calc_ease.assert_not_called]),
            (None, None, [mock_calc_int.assert_called_once,
                          mock_calc_ease.assert_called_once]),
        ]

        with self.subTest():
            for ease, interval, assert_expressions in params:
                ProblemLogCreator.create(problem_id=1, result=Result.NO_IDEA,
                                         ease=ease, interval=interval)

                for assert_expr in assert_expressions:
                    assert_expr()

    @patch.object(ProblemLogCreator, attribute='validate_problem_id')
    @patch.object(ProblemLogCreator, attribute='validate_result')
    @patch.object(ProblemLogCreator, attribute='validate_or_create_timestamp')
    def test_create_all_validators_called(self, mock_val_ts, mock_val_result,
                                          mock_val_problem_id):
        pl = ProblemLogCreator.create(last_log=None,
                                      problem_id=1,
                                      result=Result.NO_IDEA)
        self.assertIsInstance(pl, ProblemLog)
        mock_val_ts.assert_called_once()
        mock_val_result.assert_called_once()
        mock_val_problem_id.assert_called_once()

    def test_calc_ease(self):
        last_log = ProblemLogCreator.create(
            last_log=None,
            problem_id=1,
            result=Result.KNEW_BY_HEART)
        last_log.ease = 1

        test_params = [
            (last_log, Result.KNEW_BY_HEART, 1.5),
            (last_log, Result.SOLVED_OPTIMALLY_IN_UNDER_25, 1),
            (last_log, Result.SOLVED_OPTIMALLY_SLOWER, 0.5),
            (last_log, 'any_other_result', DEFAULT_EASE),
            (None, Result.KNEW_BY_HEART, DEFAULT_EASE),
        ]

        for last_log, result, expected_ease in test_params:
            with self.subTest():
                new_ease = ProblemLogCreator.calc_ease(last_log=last_log,
                                                       result=result)
                self.assertAlmostEqual(expected_ease, new_ease)

    def test_calc_interval(self):
        last_log = ProblemLogCreator.create(
            last_log=None,
            problem_id=1,
            result=Result.KNEW_BY_HEART)
        last_log.interval = 50

        test_params = [
            ('any_ease', None, Result.KNEW_BY_HEART, 21),
            ('any_ease', None, Result.SOLVED_OPTIMALLY_IN_UNDER_25, 14),
            ('any_ease', None, Result.SOLVED_OPTIMALLY_SLOWER, 3),
            (1.5, last_log, Result.SOLVED_OPTIMALLY_SLOWER, 75),
            (1.5, last_log, Result.SOLVED_OPTIMALLY_WITH_HINT,
             DEFAULT_INTERVAL),
            ('any_ease', None, Result.SOLVED_OPTIMALLY_WITH_HINT,
             DEFAULT_INTERVAL),
        ]

        for ease, last_log, result, expected_interval in test_params:
            with self.subTest():
                new_interval = ProblemLogCreator.calc_interval(
                    ease=ease, last_log=last_log, result=result)

                self.assertAlmostEqual(expected_interval, new_interval)

    def test_validate_problem_id(self):
        self.assertEqual(1,
                         ProblemLogCreator.validate_problem_id(problem_id=1))

    def test_validate_problem_id_raises_wrong_type(self):
        with self.assertRaises(TypeError) as context:
            ProblemLogCreator.validate_problem_id(problem_id='1')  # noqa

        self.assertEqual(str(context.exception),
                         "problem_id should be of type 'int'!")

    def test_validate_result(self):
        self.assertEqual(
            Result.NO_IDEA,
            ProblemLogCreator.validate_result(result=Result.NO_IDEA))

    def test_validate_result_raises_wrong_type(self):
        with self.assertRaises(TypeError) as context:
            ProblemLogCreator.validate_result(result=1)  # noqa

        self.assertEqual(str(context.exception),
                         "result should be of type 'Result'!")

    def test_create_timestamp(self):
        ts_before = dt.datetime.now(tz=gettz('UTC'))
        ts = ProblemLogCreator.validate_or_create_timestamp(ts=None)
        ts_after = dt.datetime.now(tz=gettz('UTC'))

        self.assertGreaterEqual(ts, ts_before)
        self.assertLessEqual(ts, ts_after)

    def test_validate_timestamp(self):
        ts = dt.datetime(2021, 3, 10)
        self.assertEqual(ts, ProblemLogCreator.validate_or_create_timestamp(
            ts=ts))

    def test_validate_timestamp_raises_wrong_type(self):
        with self.assertRaises(TypeError) as context:
            ProblemLogCreator.validate_or_create_timestamp(ts='2021-01-03')  # noqa

        self.assertEqual(
            str(context.exception),
            f"timestamp should be of type dt.datetime, but is <class 'str'>!")
