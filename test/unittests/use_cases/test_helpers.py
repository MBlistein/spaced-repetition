import datetime as dt
import unittest

from spaced_repetition.use_cases.helpers import (deserialize_ts,
                                                 serialize_ts,
                                                 TS_FORMAT)


class TestTimestampSerialization(unittest.TestCase):
    def test_deserialize_ts(self):
        self.assertEqual(deserialize_ts(ts_str="2021-06-30 10:30:45"),
                         dt.datetime(2021, 6, 30, 10, 30, 45))

    def test_serialize_ts(self):
        self.assertEqual(serialize_ts(ts=dt.datetime(2021, 6, 30, 10, 30, 45)),
                         "2021-06-30 10:30:45")
