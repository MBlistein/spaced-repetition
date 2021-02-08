from enum import Enum
from typing import List, Union

from dataclasses import dataclass


MAX_LINK_LENGTH = 255
MAX_NAME_LENGTH = 100
MAX_TAG_LENGTH = 20


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


class ProblemCreator:
    """Each of the validator methods return a 3-tuple:
        * idx 0: an integer if input was valid, None otherwise
        * idx 1: None if input was valid, error message (str) otherwise,
        * idx 2: optional validation message (str) or None
    """
    @classmethod
    def create_problem(cls, name: str,
                       difficulty: Difficulty,
                       tags: List[str],
                       link: str = None):
        return Problem(
            difficulty=difficulty,
            link=cls.validate_link(link),
            name=cls.validate_name(name),
            tags=cls.validate_tags(tags))

    @staticmethod
    def validate_link(link: str) -> Union[str, None]:
        if len(link) == 0:
            return None
        if len(link) <= MAX_LINK_LENGTH:
            return link
        raise ValueError(f"Link too long, max length = {MAX_LINK_LENGTH} chars.")

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
