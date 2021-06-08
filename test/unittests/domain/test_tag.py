import unittest
from unittest.mock import patch

from spaced_repetition.domain.tag import (MAX_TAG_LENGTH,
                                          Tag,
                                          TagCreator,
                                          validate_tag_list)

# pylint: disable=no-self-use


class TestTagCreator(unittest.TestCase):
    def test_create(self):
        tag = TagCreator.create(
            experience_target=2,
            name='test-tag-2',
            tag_id=22
        )

        self.assertEqual(tag,
                         Tag(experience_target=2,
                             name='test-tag-2',
                             tag_id=22))

    def test_validate_name(self):
        with patch('spaced_repetition.domain.tag.validate_param') as mock:
            mock.return_value = 'validate_input_return_val'
            self.assertEqual(TagCreator.validate_name(name='valid tag'),
                             'validate_input_return_val')

            mock.assert_called_once_with(param='valid tag',
                                         max_length=MAX_TAG_LENGTH,
                                         label='Tag')

    def test_validate_experience_target_wrong_type(self):
        with self.assertRaises(TypeError):
            TagCreator.validate_experience_target('1')

    def test_validate_experience_target_value_range(self):
        for value, error_msg in [
            (0, "Tag.experience_target should be between 1 and 15, but is 0."),
            (16, "Tag.experience_target should be between 1 and 15, but is 16."),
        ]:
            with self.subTest(value=value, error_msg=error_msg):
                with self.assertRaises(ValueError) as context:
                    TagCreator.validate_experience_target(value)

                self.assertEqual(error_msg,
                                 str(context.exception))

    @patch.object(TagCreator, attribute='validate_name')
    @patch.object(TagCreator, attribute='validate_experience_target')
    def test_all_validators_called(self, mock_validate_experience_target,
                                   mock_validate_name):
        TagCreator.create(name='tag1',
                          experience_target=5)

        mock_validate_name.assert_called_once()
        mock_validate_experience_target.assert_called_once()


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
