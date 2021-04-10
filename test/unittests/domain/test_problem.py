
import unittest
from unittest.mock import patch

from spaced_repetition.domain.problem import Difficulty, ProblemCreator

MAX_URL_LENGTH = 255
MAX_NAME_LENGTH = 100
MAX_TAG_LENGTH = 20


class TestProblemCreator(unittest.TestCase):
    def test_validate_url_text(self):
        with patch('spaced_repetition.domain.problem.validate_param') as mock:
            ProblemCreator.validate_url(url='valid-url.com')

            mock.assert_called_once_with(param='valid-url.com',
                                         max_length=MAX_URL_LENGTH,
                                         label='URL',
                                         empty_allowed=True)

    def test_validate_url_empty(self):
        with patch('spaced_repetition.domain.problem.validate_param') as mock:
            ProblemCreator.validate_url(url=None)

            mock.assert_called_once_with(param='',
                                         max_length=MAX_URL_LENGTH,
                                         label='URL',
                                         empty_allowed=True)

    def test_validate_name(self):
        with patch('spaced_repetition.domain.problem.validate_param') as mock:
            ProblemCreator.validate_name(name='valid name')

            mock.assert_called_once_with(param='valid name',
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
        with patch('spaced_repetition.domain.problem.validate_param') as mock:
            ProblemCreator.validate_tags(tags=['test_tag'])

            mock.assert_called_once_with(param='test_tag',
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

    @patch.object(ProblemCreator, attribute='validate_difficulty')
    @patch.object(ProblemCreator, attribute='validate_name')
    @patch.object(ProblemCreator, attribute='validate_tags')
    @patch.object(ProblemCreator, attribute='validate_url')
    def test_all_validators_called(self, mock_val_url, mock_val_tags,
                                   mock_val_name, mock_val_difficulty):
        ProblemCreator.create(name='fake',
                              difficulty='fake',
                              tags='fake',
                              problem_id='fake',
                              url='fake')

        mock_val_difficulty.assert_called_once()
        mock_val_name.assert_called_once()
        mock_val_tags.assert_called_once()
        mock_val_url.assert_called_once()
