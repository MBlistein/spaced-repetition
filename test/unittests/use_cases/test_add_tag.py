
import unittest
from unittest.mock import Mock, patch

from spaced_repetition.domain.tag import TagCreator
from spaced_repetition.use_cases.add_tag import TagAdder


class TestTagAdder(unittest.TestCase):
    def setUp(self) -> None:
        self.tag = TagCreator.create('new_tag')

    @patch.object(TagAdder, '_assert_is_unique')
    def test_add_tag(self, mock_assert_unique):
        t_a = TagAdder(db_gateway=Mock(), presenter=Mock())

        t_a.add_tag(name=self.tag.name)

        mock_assert_unique.assert_called_once_with(tag=self.tag)
        t_a.repo.create_tag.assert_called_once_with(tag=self.tag)  # noqa

    def test_assert_is_unique_raises(self):
        t_a = TagAdder(db_gateway=Mock(), presenter=Mock())
        t_a.repo.tag_exists.return_value = True

        with self.assertRaises(ValueError) as context:
            t_a._assert_is_unique(tag=self.tag)

        self.assertEqual("Tag with name 'new_tag' already exists!",
                         str(context.exception))

    def test_assert_is_unique(self):
        t_a = TagAdder(db_gateway=Mock(), presenter=Mock())
        t_a.repo.tag_exists.return_value = False
        t_a._assert_is_unique(tag=self.tag)
