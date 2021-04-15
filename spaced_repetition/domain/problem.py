from enum import Enum
from typing import List, Union

from dataclasses import dataclass

from .domain_helpers import validate_param


MAX_URL_LENGTH = 255
MAX_NAME_LENGTH = 100
MAX_TAG_LENGTH = 20


class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


@dataclass
class Problem:
    difficulty: Difficulty
    name: str
    problem_id: Union[int, None]
    tags: List[str]  # TODO: make List[Tag]
    url: Union[str, None]


class ProblemCreator:
    @classmethod
    def create(cls, name: str,          # pylint: disable=too-many-arguments
               difficulty: Difficulty,
               tags: List[str],
               problem_id: int = None,
               url: str = None):
        return Problem(
            difficulty=cls.validate_difficulty(difficulty),
            name=cls.validate_name(name),
            problem_id=problem_id,
            tags=cls.validate_tags(tags),
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
    def validate_tags(tags: List[str]) -> List[str]:
        if not isinstance(tags, list):
            raise TypeError("Tags must be a list of strings.")

        for tag in tags:
            if not isinstance(tag, str):
                raise TypeError("Tags must be strings.")

            validate_param(param=tag, max_length=MAX_TAG_LENGTH, label='Tag')

        if len(tags) == 0:
            raise ValueError("Provide at least one tag.")
        return tags

    @staticmethod
    def validate_url(url: Union[str, None]) -> Union[str, None]:
        return validate_param(param=url or '', max_length=MAX_URL_LENGTH, label='URL',
                              empty_allowed=True)
