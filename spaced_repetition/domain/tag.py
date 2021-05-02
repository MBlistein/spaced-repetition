from dataclasses import dataclass
from typing import List, Union

from .domain_helpers import validate_param

MAX_TAG_LENGTH = 20


@dataclass
class Tag:
    name: str
    tag_id: Union[int, None] = None


class TagCreator:
    @classmethod
    def create(cls, name: str, tag_id: int = None):
        return Tag(name=cls.validate_name(name),
                   tag_id=tag_id)

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
