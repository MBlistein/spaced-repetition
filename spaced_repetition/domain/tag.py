from dataclasses import dataclass
from typing import List, Union

from .domain_helpers import validate_param

MAX_TAG_LENGTH = 25
MIN_EXPERIENCE_TARGET = 1
MAX_EXPERIENCE_TARGET = 15


@dataclass
class Tag:
    experience_target: int  # number of problems to solve for full experience
    name: str
    tag_id: Union[int, None] = None


class TagCreator:
    @classmethod
    def create(cls, name: str, experience_target: int = 5, tag_id: int = None):
        return Tag(experience_target=experience_target,
                   name=cls.validate_name(name),
                   tag_id=tag_id)

    @staticmethod
    def validate_experience_target(experience_target: int) -> int:
        if not isinstance(experience_target, int):
            raise TypeError("Tag.experience_target must be an integer!")

        if not MIN_EXPERIENCE_TARGET <= experience_target <= MAX_EXPERIENCE_TARGET:
            raise ValueError("Tag.experience_target should be between "
                             f"{MIN_EXPERIENCE_TARGET} and {MAX_EXPERIENCE_TARGET}"
                             f", but is {experience_target}.")
        return experience_target

    @staticmethod
    def validate_name(name: str) -> str:
        return validate_param(param=name,
                              max_length=MAX_TAG_LENGTH,
                              label='Tag')


def validate_tag_list(tags: List[Tag]) -> List[Tag]:
    if not isinstance(tags, list):
        raise TypeError("Tags must be a list of Tags.")

    if len(tags) == 0:
        raise ValueError("Provide at least one tag.")

    if not all(isinstance(tag, Tag) for tag in tags):
        raise TypeError("Expected a list of Tag instances!")

    return tags
