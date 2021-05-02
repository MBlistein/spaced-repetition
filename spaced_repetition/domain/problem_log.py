""" ProblemLogs trace problem execution over time and contain information
regarding the optimal repetition intervals for each problem. This information
can be used to schedule repetition dates according to the SuperMemo2 algorithm,
see: https://en.wikipedia.org/wiki/SuperMemo

Calculation of a problem's ease and interval is adapted from the original:
  - ease: simpler logic (linear curve) with a stronger incline, but similarly
          linear effect as the original
  - interval: Custom default intervals depending on initial problem result,
              otherwise similar logic
"""

import datetime as dt
from dataclasses import dataclass
from enum import Enum, unique
from typing import List, Union

from dateutil.tz import gettz

from .domain_helpers import validate_param
from .tag import Tag, validate_tag_list


MAX_COMMENT_LENGTH = 255


@unique
class Result(Enum):
    NO_IDEA = 0
    SOLVED_SUBOPTIMALLY = 1
    SOLVED_OPTIMALLY_WITH_HINT = 2
    SOLVED_OPTIMALLY_SLOWER = 3
    SOLVED_OPTIMALLY_IN_UNDER_25 = 4
    KNEW_BY_HEART = 5


@dataclass(frozen=True)
class ProblemLog:
    problem_id: int
    result: Result
    tags: List[Tag]
    timestamp: dt.datetime
    comment: str = ''


class ProblemLogCreator:
    @classmethod
    def create(cls,                      # pylint: disable=too-many-arguments
               problem_id: int,
               result: Result,
               tags: List[Tag],
               comment: str = '',
               timestamp: dt.datetime = None):

        return ProblemLog(
            comment=cls.validate_comment(comment),
            problem_id=cls.validate_problem_id(problem_id),
            result=cls.validate_result(result),
            tags=validate_tag_list(tags),
            timestamp=cls.validate_or_create_timestamp(timestamp))

    @staticmethod
    def validate_comment(comment: str):
        return validate_param(param=comment, max_length=MAX_COMMENT_LENGTH,
                              label='Comment', empty_allowed=True)

    @staticmethod
    def validate_problem_id(problem_id: int) -> int:
        if not isinstance(problem_id, int):
            raise TypeError("problem_id should be of type 'int'!")
        return problem_id

    @staticmethod
    def validate_result(result: Result) -> Result:
        if not isinstance(result, Result):
            raise TypeError("result should be of type 'Result'!")
        return result

    @staticmethod
    def validate_or_create_timestamp(ts: Union[dt.datetime, None]) -> dt.datetime:
        if ts is None:
            return dt.datetime.now(tz=gettz('UTC'))

        if not isinstance(ts, dt.datetime):
            raise TypeError(
                f'timestamp should be of type dt.datetime, but is {type(ts)}!')
        return ts
