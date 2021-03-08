
import unittest
from unittest.mock import Mock, patch

from spaced_repetition.domain.problem import Difficulty, ProblemCreator

MAX_URL_LENGTH = 255
MAX_NAME_LENGTH = 100
MAX_TAG_LENGTH = 20


class TestProblemCreator(unittest.TestCase):
    def test_validate_url_none(self):
        self.assertIsNone(ProblemCreator.validate_url(url=None))

    def test_validate_url_text(self):
        with patch('spaced_repetition.domain.problem.validate_input') as mock:
            ProblemCreator.validate_url(url='valid-url.com')

            mock.assert_called_once_with(inpt='valid-url.com',
                                         max_length=MAX_URL_LENGTH,
                                         label='URL')

    def test_validate_name(self):
        with patch('spaced_repetition.domain.problem.validate_input') as mock:
            ProblemCreator.validate_name(name='valid name')

            mock.assert_called_once_with(inpt='valid name',
                                         max_length=MAX_NAME_LENGTH,
                                         label='Name')

    def test_validate_tags(self):
        self.assertEqual(ProblemCreator.validate_tags(tags=['tag1', 'tag2']),
                         ['tag1', 'tag2'])

    def test_validate_tags_raises_input_is_not_list(self):
        with self.assertRaises(TypeError) as context:
            ProblemCreator.validate_tags(tags="tag1 tag2")

        self.assertEqual(str(context.exception),
                         "Tags must be a list of strings.")

    def test_validate_tags_empty(self):
        with self.assertRaises(ValueError) as context:
            ProblemCreator.validate_tags(tags=[])

        self.assertEqual(str(context.exception),
                         "Provide at least one tag.")

    def test_validate_tag_input_validated(self):
        with patch('spaced_repetition.domain.problem.validate_input') as mock:
            ProblemCreator.validate_tags(tags=['test_tag'])

            mock.assert_called_once_with(inpt='test_tag',
                                         max_length=MAX_TAG_LENGTH,
                                         label='Tag')

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
