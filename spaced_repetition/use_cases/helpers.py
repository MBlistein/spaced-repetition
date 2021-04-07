"""Time serialization"""

import datetime as dt

TS_FORMAT = '%Y-%m-%d %H:%M:%S'


def deserialize_ts(ts_str: str):
    return dt.datetime.strptime(ts_str, TS_FORMAT)


def serialize_ts(ts: dt.datetime):
    return dt.datetime.strftime(ts, TS_FORMAT)
