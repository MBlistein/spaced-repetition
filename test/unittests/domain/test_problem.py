
import unittest
from unittest.mock import patch

from spaced_repetition.domain.problem import Difficulty, ProblemCreator
from spaced_repetition.domain.tag import TagCreator

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
    @patch('spaced_repetition.domain.problem.validate_tag_list')
    @patch.object(ProblemCreator, attribute='validate_url')
    def test_all_validators_called(self, mock_val_url, mock_val_tags,
                                   mock_val_name, mock_val_difficulty):
        tag = TagCreator.create(name='test-tag')
        ProblemCreator.create(name='fake',
                              difficulty=Difficulty.EASY,
                              tags=[tag],
                              problem_id=1,
                              url='fake')

        mock_val_difficulty.assert_called_once()
        mock_val_name.assert_called_once()
        mock_val_tags.assert_called_once_with([tag])
        mock_val_url.assert_called_once()
