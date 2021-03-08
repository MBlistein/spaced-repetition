import datetime as dt
from enum import Enum
from typing import Union

from dataclasses import dataclass


class Result(Enum):
    SOLVED_OPTIMALLY_IN_UNDER_25 = 0
    SOLVED_SUBOPTIMALLY_IN_UNDER_25 = 1
    SOLVED_OPTIMALLY_SLOWER = 2
    SOLVED_SUBOPTIMALLY_SLOWER = 3
    SOLVED_OPTIMALLY_WITH_HINT = 4
    SOLVED_SUBOPTIMALLY_WITH_HINT = 5
    NO_IDEA = 6
    NEVER_TRIED = 7


@dataclass
class ProblemLog:
    problem_id: int
    result: Result
    timestamp: Union[dt.datetime, None] = None
