from enum import Enum
from typing import List, Union

from dataclasses import dataclass


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
    tags: List[str]
    url: Union[str, None]


class ProblemCreator:
    @classmethod
    def create_problem(cls, name: str,
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
        if type(difficulty) is not Difficulty:
            raise TypeError('difficulty should be of type Difficulty')
        return difficulty

    @staticmethod
    def validate_name(name: str) -> str:
        if len(name) < 1:
            raise ValueError("Name cannot be empty.")
        if len(name) > MAX_NAME_LENGTH:
            raise ValueError(
                f"Name too long, max length = {MAX_NAME_LENGTH} chars.")
        return name

    @staticmethod
    def validate_tags(tags: List[str]) -> List[str]:
        if not isinstance(tags, list):
            raise TypeError("Tags must be a list of strings.")

        for tag in tags:
            if not isinstance(tag, str):
                raise TypeError("Tags must be strings.")
            if len(tag) > MAX_TAG_LENGTH:
                raise ValueError(
                    f"Each tag must be at most {MAX_TAG_LENGTH} chars long.")

        if len(tags) == 0:
            raise ValueError("Provide at least one tag.")
        return tags

    @staticmethod
    def validate_url(url: Union[str, None]) -> Union[str, None]:
        if url is None or len(url) == 0:
            return None
        if len(url) <= MAX_URL_LENGTH:
            return url
        raise ValueError(f"Url too long, max length = {MAX_URL_LENGTH} chars.")
