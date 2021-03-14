import datetime as dt
from enum import Enum, unique
from typing import Union

from dataclasses import dataclass


@unique
class Result(Enum):
    KNEW_BY_HEART = 0
    SOLVED_OPTIMALLY_IN_UNDER_25 = 1
    SOLVED_OPTIMALLY_SLOWER = 2
    SOLVED_OPTIMALLY_WITH_HINT = 3
    SOLVED_SUBOPTIMALLY = 4
    NO_IDEA = 5


@dataclass
class ProblemLog:
    problem_id: int
    result: Result
    timestamp: Union[dt.datetime, None] = None
