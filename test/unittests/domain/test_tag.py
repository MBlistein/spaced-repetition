import unittest
from unittest.mock import patch

from spaced_repetition.domain.tag import (MAX_TAG_LENGTH,
                                          TagCreator,
                                          validate_tag_list)

# pylint: disable=no-self-use


class TestTagCreator(unittest.TestCase):
    def test_validate_name(self):
        with patch('spaced_repetition.domain.tag.validate_param') as mock:
            mock.return_value = 'validate_input_return_val'
            self.assertEqual(TagCreator.validate_name(name='valid tag'),
                             'validate_input_return_val')

            mock.assert_called_once_with(param='valid tag',
                                         max_length=MAX_TAG_LENGTH,
                                         label='Tag')

    @patch.object(TagCreator, attribute='validate_name')
    def test_all_validators_called(self, mock_validate_name):
        TagCreator.create(name='tag1')

        mock_validate_name.assert_called_once()


class TestHelpers(unittest.TestCase):
    def test_validate_tag_list_raises_input_is_not_list(self):
        with self.assertRaises(TypeError) as context:
            validate_tag_list(tags="tag1 tag2")

        self.assertEqual(str(context.exception),
                         "Tags must be a list of Tags.")

    def test_validate_tag_list_raises_is_not_tag_instance(self):
        with self.assertRaises(TypeError) as context:
            validate_tag_list(tags=["tag1"])

        self.assertEqual(str(context.exception),
                         "Expected a list of Tag instances!")

    def test_validate_tag_list_empty(self):
        with self.assertRaises(ValueError) as context:
            validate_tag_list(tags=[])

        self.assertEqual(str(context.exception),
                         "Provide at least one tag.")
