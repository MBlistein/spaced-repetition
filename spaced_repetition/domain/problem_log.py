import datetime as dt
from enum import Enum
from typing import Union

from dataclasses import dataclass


class Result(Enum):
    SOLVED_OPTIMALLY_IN_UNDER_25 = 0
    SOLVED_OPTIMALLY_SLOWER = 1
    SOLVED_OPTIMALLY_WITH_HINT = 2
    SOLVED_SUBOPTIMALLY_IN_UNDER_25 = 3
    SOLVED_SUBOPTIMALLY_SLOWER = 4
    SOLVED_SUBOPTIMALLY_WITH_HINT = 5
    NO_IDEA = 6


@dataclass
class ProblemLog:
    problem_id: int
    result: Result
    timestamp: Union[dt.datetime, None] = None
