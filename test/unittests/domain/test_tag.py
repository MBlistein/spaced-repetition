import unittest
from unittest.mock import Mock

from spaced_repetition.domain.tag import TagCreator

MAX_TAG_LENGTH = 10


class TestTagCreator(unittest.TestCase):
    def test_validate_name(self):
        self.assertEqual(TagCreator.validate_name(name='tag1'),
                         'tag1')

    def test_validate_name_raises_empty(self):
        with self.assertRaises(ValueError) as context:
            TagCreator.validate_name(name='')

        self.assertEqual(str(context.exception),
                         "Tag name cannot be empty.")

    def test_validate_name_raises_too_long(self):
        with self.assertRaises(ValueError) as context:
            TagCreator.validate_name(name='a' * (MAX_TAG_LENGTH + 1))

        self.assertEqual(str(context.exception),
                         f"Tag name too long, max length = {MAX_TAG_LENGTH} chars.")

    def test_all_validators_called(self):
        class FakeTagCreator(TagCreator):
            pass

        FakeTagCreator.validate_name = Mock()

        FakeTagCreator.create_tag(name='tag1')

        FakeTagCreator.validate_name.assert_called_once()
