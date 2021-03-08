import unittest
from unittest.mock import patch

from spaced_repetition.domain.tag import TagCreator

MAX_TAG_LENGTH = 10


class TestTagCreator(unittest.TestCase):
    def test_validate_name(self):
        with patch('spaced_repetition.domain.tag.validate_input') as mock:
            mock.return_value = 'validate_input_return_val'
            self.assertEqual(TagCreator.validate_name(name='valid tag'),
                             'validate_input_return_val')

            mock.assert_called_once_with(inpt='valid tag',
                                         max_length=MAX_TAG_LENGTH,
                                         label='Tag')

    @patch.object(TagCreator, attribute='validate_name')
    def test_all_validators_called(self, mock_validate_name):
        TagCreator.create_tag(name='tag1')

        mock_validate_name.assert_called_once()
