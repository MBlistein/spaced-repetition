import datetime as dt
import unittest
from unittest.mock import patch

from dateutil.tz import gettz

from spaced_repetition.domain.problem_log import (ProblemLog,
                                                  ProblemLogCreator,
                                                  Result)
from spaced_repetition.domain.tag import TagCreator


class TestProblemLogCreator(unittest.TestCase):
    def setUp(self) -> None:
        self.tag = TagCreator.create(name='test-tag', experience_target=5)

    @patch.object(ProblemLogCreator, attribute='validate_comment')
    @patch.object(ProblemLogCreator, attribute='validate_problem_id')
    @patch.object(ProblemLogCreator, attribute='validate_result')
    @patch.object(ProblemLogCreator, attribute='validate_or_create_timestamp')
    @patch('spaced_repetition.domain.problem_log.validate_tag_list')
    def test_create_all_validators_called(self, mock_val_tags, mock_val_ts,  # pylint: disable=too-many-arguments
                                          mock_val_result,
                                          mock_val_problem_id, mock_val_comment):
        p_l = ProblemLogCreator.create(comment='test-comment',
                                       problem_id=1,
                                       result=Result.NO_IDEA,
                                       tags=[self.tag])
        self.assertIsInstance(p_l, ProblemLog)
        mock_val_tags.assert_called_once_with([self.tag])
        mock_val_ts.assert_called_once()
        mock_val_result.assert_called_once()
        mock_val_problem_id.assert_called_once()
        mock_val_comment.assert_called_once()

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
            "timestamp should be of type dt.datetime, but is <class 'str'>!")

    def test_validate_comment_raises_too_long(self):
        with self.assertRaises(ValueError) as context:
            ProblemLogCreator.validate_comment(comment='a' * 256)

        self.assertEqual(
            str(context.exception),
            "Comment too long, max length = 255 chars.")
