from dataclasses import dataclass
from typing import Union


MAX_TAG_LENGTH = 10


@dataclass
class Tag:
    name: str
    tag_id: Union[int, None] = None


class TagCreator:
    @classmethod
    def create_tag(cls, name: str, tag_id: int = None):
        return Tag(name=cls.validate_name(name),
                   tag_id=tag_id)

    @staticmethod
    def validate_name(name: str) -> str:
        if len(name) < 1:
            raise ValueError("Tag name cannot be empty.")
        if len(name) > MAX_TAG_LENGTH:
            raise ValueError(
                f"Tag name too long, max length = {MAX_TAG_LENGTH} chars.")
        return name
