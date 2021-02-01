from enum import Enum
from typing import List

from dataclasses import dataclass


class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


@dataclass
class Problem:
    name: str
    link: str
    tags: List[str]
    difficulty: Difficulty
