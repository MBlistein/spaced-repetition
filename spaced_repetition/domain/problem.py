from enum import Enum
from typing import List, Union

from dataclasses import dataclass

from .domain_helpers import validate_param
from .tag import Tag, validate_tag_list


MAX_URL_LENGTH = 255
MAX_NAME_LENGTH = 100


class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


@dataclass
class Problem:
    difficulty: Difficulty
    name: str
    problem_id: Union[int, None]
    tags: List[Tag]
    url: Union[str, None]


class ProblemCreator:
    @classmethod
    def create(cls, name: str,          # pylint: disable=too-many-arguments
               difficulty: Difficulty,
               tags: List[Tag],
               problem_id: int = None,
               url: str = None):
        return Problem(
            difficulty=cls.validate_difficulty(difficulty),
            name=cls.validate_name(name),
            problem_id=problem_id,
            tags=validate_tag_list(tags),
            url=cls.validate_url(url))

    @staticmethod
    def validate_difficulty(difficulty: Difficulty) -> Difficulty:
        if not isinstance(difficulty, Difficulty):
            raise TypeError('difficulty should be of type Difficulty')
        return difficulty

    @staticmethod
    def validate_name(name: str) -> str:
        return validate_param(param=name,
                              max_length=MAX_NAME_LENGTH,
                              label='Name')

    @staticmethod
    def validate_url(url: Union[str, None]) -> Union[str, None]:
        return validate_param(param=url or '', max_length=MAX_URL_LENGTH, label='URL',
                              empty_allowed=True)
