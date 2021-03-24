from dataclasses import dataclass
from typing import Union

from .domain_helpers import validate_param

MAX_TAG_LENGTH = 10


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
