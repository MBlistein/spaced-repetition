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


DEFAULT_EASE = 2.5
DEFAULT_INTERVAL = 1


@unique
class Result(Enum):
    NO_IDEA = 0
    SOLVED_SUBOPTIMALLY = 1
    SOLVED_OPTIMALLY_WITH_HINT = 2
    SOLVED_OPTIMALLY_SLOWER = 3
    SOLVED_OPTIMALLY_IN_UNDER_25 = 4
    KNEW_BY_HEART = 5


@dataclass
class ProblemLog:
    ease: float  # factor for spacing interval
    interval: int  # in days
    problem_id: int
    result: Result
    timestamp: dt.datetime


class ProblemLogCreator:
    @classmethod
    def create(cls,
               problem_id: int,
               result: Result,
               ease: float = None,
               interval: int = None,
               last_log: ProblemLog = None,
               timestamp: dt.datetime = None):

        ease = ease or cls.calc_ease(last_log=last_log, result=result)
        interval = interval or cls.calc_interval(ease=ease,
                                                 last_log=last_log,
                                                 result=result)
        return ProblemLog(
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
            return ease + 0.5
        if result == Result.SOLVED_OPTIMALLY_IN_UNDER_25:
            return ease
        if result == Result.SOLVED_OPTIMALLY_SLOWER:
            return ease - 0.5

        # did not know the optimal solution (without hint) -> start over
        return DEFAULT_EASE

    @staticmethod
    def calc_interval(ease: float, last_log: Union[ProblemLog, None],
                      result: Result) -> int:
        if result.value >= Result.SOLVED_OPTIMALLY_SLOWER.value:
            # eventually reached the optimal result without help
            if not last_log:
                # do the problem for the first time -> set new defaults
                if result == Result.KNEW_BY_HEART:
                    return 21
                if result == Result.SOLVED_OPTIMALLY_IN_UNDER_25:
                    return 14
                if result == Result.SOLVED_OPTIMALLY_SLOWER:
                    return 3
                raise ValueError(f"Result '{result.name}' unknown!")

            return round(last_log.interval * ease)

        # did not know the optimal solution (without hint) -> start over
        return DEFAULT_INTERVAL

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
