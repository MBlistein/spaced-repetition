
import unittest

from spaced_repetition.controllers.cli_controller import (_format_difficulty,
                                                          _format_tags)
from spaced_repetition.domain.problem import Difficulty


class TestCliController(unittest.TestCase):
    def test_format_difficulty(self):
        self.assertEqual(_format_difficulty(difficulty='1'),
                         Difficulty.EASY)

    def test_format_difficulty_unknown_difficulty(self):
        with self.assertRaises(ValueError) as context:
            _format_difficulty(difficulty='0')

        self.assertEqual(str(context.exception),
                         "0 is not a valid Difficulty")

    def test_format_tags(self):
        self.assertEqual(['tag1', 'tag2'],
                         _format_tags('tag1 tag2'))
