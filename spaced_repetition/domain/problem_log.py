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
from typing import Union

from dateutil.tz import gettz

from .domain_helpers import validate_param


DEFAULT_EASE = 2.5
EASE_DELTA = 0.12
INTERVAL_KNEW_BY_HEART = 21
INTERVAL_SOLVED_OPTIMALLY_IN_UNDER_25 = 14
INTERVAL_SOLVED_OPTIMALLY_SLOWER = 7
INTERVAL_NON_OPTIMAL_SOLUTION = 3
MAX_COMMENT_LENGTH = 255
MINIMUM_EASE = 1.3


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
    ease: float  # factor for spacing interval
    interval: int  # in days
    problem_id: int
    result: Result
    timestamp: dt.datetime
    comment: str = ''


class ProblemLogCreator:
    @classmethod
    def create(cls,                      # pylint: disable=too-many-arguments
               problem_id: int,
               result: Result,
               comment: str = '',
               ease: float = None,
               interval: int = None,
               last_log: ProblemLog = None,
               timestamp: dt.datetime = None):

        ease = ease or cls.calc_ease(last_log=last_log, result=result)
        interval = interval or cls.calc_interval(ease=ease,
                                                 last_log=last_log,
                                                 result=result)
        return ProblemLog(
            comment=cls.validate_comment(comment),
            ease=ease,
            interval=interval,
            problem_id=cls.validate_problem_id(problem_id),
            result=cls.validate_result(result),
            timestamp=cls.validate_or_create_timestamp(timestamp))

    @staticmethod
    def calc_ease(last_log: Union[ProblemLog, None], result: Result) -> float:
        if not last_log:
            return DEFAULT_EASE

        ease = last_log.ease
        if result == Result.KNEW_BY_HEART:
            ease += EASE_DELTA
        elif result == Result.SOLVED_OPTIMALLY_IN_UNDER_25:
            pass
        elif result == Result.SOLVED_OPTIMALLY_SLOWER:
            ease -= EASE_DELTA
        else:
            # did not know the optimal solution (without hint) -> start over
            ease = DEFAULT_EASE

        ease = max(ease, MINIMUM_EASE)

        return ease

    @staticmethod
    def calc_interval(ease: float, last_log: Union[ProblemLog, None],
                      result: Result) -> int:
        if result.value >= Result.SOLVED_OPTIMALLY_SLOWER.value:
            # eventually reached the optimal result without help
            if not last_log:
                # did the problem for the first time -> set new defaults
                if result == Result.KNEW_BY_HEART:
                    return INTERVAL_KNEW_BY_HEART
                if result == Result.SOLVED_OPTIMALLY_IN_UNDER_25:
                    return INTERVAL_SOLVED_OPTIMALLY_IN_UNDER_25
                if result == Result.SOLVED_OPTIMALLY_SLOWER:
                    return INTERVAL_SOLVED_OPTIMALLY_SLOWER
                raise ValueError(f"Result '{result.name}' unknown!")

            return round(last_log.interval * ease)

        # did not know the optimal solution (without hint) -> start over
        return INTERVAL_NON_OPTIMAL_SOLUTION

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
