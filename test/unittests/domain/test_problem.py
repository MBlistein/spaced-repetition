
import unittest
from unittest.mock import Mock

from spaced_repetition.domain.problem import (Difficulty,
                                              ProblemCreator)

MAX_LINK_LENGTH = 255
MAX_NAME_LENGTH = 100
MAX_TAG_LENGTH = 20


class TestProblemCreator(unittest.TestCase):
    def test_validate_difficulty(self):
        for num in range(1, 4):
            self.assertEqual(ProblemCreator.validate_difficulty(num),
                             Difficulty(num))

    def test_validate_difficulty_invalid_int(self):
        with self.assertRaises(ValueError) as context:
            ProblemCreator.validate_difficulty(0)

        self.assertEqual(str(context.exception),
                         "Unknown difficulty: 0.")

    def test_validate_link_raises_too_long(self):
        with self.assertRaises(ValueError) as context:
            ProblemCreator.validate_link('a' * (MAX_LINK_LENGTH + 1))

        self.assertEqual(str(context.exception),
                         f"Link too long, max length = 255 chars.")

    def test_validate_name_raises_empty(self):
        with self.assertRaises(ValueError) as context:
            ProblemCreator.validate_name('')

        self.assertEqual(str(context.exception),
                         "Name cannot be empty.")

    def test_validate_name_raises_too_long(self):
        with self.assertRaises(ValueError) as context:
            ProblemCreator.validate_name('a' * (MAX_NAME_LENGTH + 1))

        self.assertEqual(str(context.exception),
                         f"Name too long, max length = {MAX_NAME_LENGTH} chars.")

    def test_validate_tags(self):
        self.assertEqual(ProblemCreator.validate_tags(tags=['tag1', 'tag2']),
                         ['tag1', 'tag2'])

    def test_validate_tags_string_input(self):
        with self.assertRaises(TypeError) as context:
            ProblemCreator.validate_tags(tags="tag1 tag2")

        self.assertEqual(str(context.exception),
                         "Tags must be a list of strings.")

    def test_validate_tags_wrong_type(self):
        with self.assertRaises(TypeError) as context:
            ProblemCreator.validate_tags(tags=["tag1", 1])

        self.assertEqual(str(context.exception),
                         "Tags must be strings.")

    def test_validate_tags_empty(self):
        with self.assertRaises(ValueError) as context:
            ProblemCreator.validate_tags(tags=[])

        self.assertEqual(str(context.exception),
                         "Provide at least one tag.")
