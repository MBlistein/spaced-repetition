
import unittest
from unittest.mock import Mock

from spaced_repetition.domain.problem import Difficulty, ProblemCreator

MAX_URL_LENGTH = 255
MAX_NAME_LENGTH = 100
MAX_TAG_LENGTH = 20


class TestProblemCreator(unittest.TestCase):
    def test_validate_url_empty(self):
        self.assertIsNone(ProblemCreator.validate_url(url=''))

    def test_validate_url_none(self):
        self.assertIsNone(ProblemCreator.validate_url(url=None))

    def test_validate_url_raises_too_long(self):
        with self.assertRaises(ValueError) as context:
            ProblemCreator.validate_url(url='a' * (MAX_URL_LENGTH + 1))

        self.assertEqual(str(context.exception),
                         f"Url too long, max length = {MAX_URL_LENGTH} chars.")

    def test_validate_name_raises_empty(self):
        with self.assertRaises(ValueError) as context:
            ProblemCreator.validate_name(name='')

        self.assertEqual(str(context.exception),
                         "Name cannot be empty.")

    def test_validate_name_raises_too_long(self):
        with self.assertRaises(ValueError) as context:
            ProblemCreator.validate_name(name='a' * (MAX_NAME_LENGTH + 1))

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

    def test_validate_tag_raises_too_long(self):
        with self.assertRaises(ValueError) as context:
            ProblemCreator.validate_tags(tags=['a' * (MAX_TAG_LENGTH + 1)])

        self.assertEqual(str(context.exception),
                         f"Each tag must be at most {MAX_TAG_LENGTH} chars long.")

    def test_validate_difficulty(self):
        self.assertEqual(
            ProblemCreator.validate_difficulty(difficulty=Difficulty.EASY),
            Difficulty.EASY)

    def test_validate_difficulty_raises(self):
        with self.assertRaises(TypeError) as context:
            ProblemCreator.validate_difficulty(difficulty=2)

        self.assertEqual(str(context.exception),
                         'difficulty should be of type Difficulty')

    def test_all_validators_called(self):
        class FakeProblemCreator(ProblemCreator):
            pass

        FakeProblemCreator.validate_difficulty = Mock()
        FakeProblemCreator.validate_name = Mock()
        FakeProblemCreator.validate_tags = Mock()
        FakeProblemCreator.validate_url = Mock()

        FakeProblemCreator.create_problem(name='fake',
                                          difficulty='fake',
                                          tags='fake',
                                          problem_id='fake',
                                          url='fake')

        FakeProblemCreator.validate_difficulty.assert_called_once()
        FakeProblemCreator.validate_name.assert_called_once()
        FakeProblemCreator.validate_tags.assert_called_once()
        FakeProblemCreator.validate_url.assert_called_once()
