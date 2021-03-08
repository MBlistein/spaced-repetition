
import unittest
from unittest.mock import call, patch

from spaced_repetition.domain.problem import Difficulty, ProblemCreator
from spaced_repetition.domain.tag import TagCreator
from spaced_repetition.presenters.cli_presenter import CliPresenter


PROBLEM = ProblemCreator.create_problem(
    name='testname',
    difficulty=Difficulty(1),
    problem_id=1,
    tags=['test-tag'],
    url='test-url')


class TestCliPresenter(unittest.TestCase):
    def setUp(self):
        self.num_cols = 5
        self.column_widths = [5, 20, 20, 10, 25]

    def test_problem_confirmation_txt(self):
        self.assertEqual("Created Problem 'testname' with id '1' "
                         "(difficulty 'EASY', tags: test-tag)",
                         CliPresenter._problem_confirmation_txt(problem=PROBLEM))

    def test_format_entry(self):
        self.assertEqual(CliPresenter._format_entry(entry='123', max_len=5),
                         '123  ')

    def test_format_table_row(self):
        column_widths = self.column_widths
        column_widths[2] = 10  # tags
        column_widths[4] = 4   # url
        self.assertEqual(
            CliPresenter._format_table_row(
                content=['01234', '0123456789', '0123456789', '0123456', '0123'],
                column_widths=column_widths, num_cols=self.num_cols),
            '| 01234 | 0123456789           | 0123456789 | 0123456    | 0123 |')

    def test_format_table_row_raises(self):
        with self.assertRaises(ValueError) as context:
            CliPresenter._format_table_row(content=[],
                                           column_widths=self.column_widths,
                                           num_cols=self.num_cols)

        self.assertEqual(str(context.exception),
                         'Need exactly 5 entries!')

    @patch.object(CliPresenter, attribute='_format_table_row')
    def test_list_problems(self, mock_format_table_row):
        mock_format_table_row.return_value = None
        column_widths = self.column_widths
        column_widths[2] = 8  # tags
        column_widths[4] = 8   # url

        CliPresenter.list_problems(problems=[PROBLEM, PROBLEM])

        calls = [
            call(content=['Id', 'Name', 'Tags', 'Difficulty', 'URL'],
                 column_widths=column_widths, num_cols=self.num_cols),
            call(content=['1', 'testname', 'test-tag', 'EASY', 'test-url'],
                 column_widths=column_widths, num_cols=self.num_cols),
            call(content=['1', 'testname', 'test-tag', 'EASY', 'test-url'],
                 column_widths=column_widths, num_cols=self.num_cols),
        ]
        mock_format_table_row.assert_has_calls(calls)


class TestCliPresenterTags(unittest.TestCase):
    def setUp(self):
        self.num_cols = 2
        self.column_widths = [5, 10]

    @patch.object(CliPresenter, attribute='_format_table_row')
    def test_list_tags(self, mock_format_table_row):
        mock_format_table_row.return_value = None

        tag = TagCreator.create_tag(name='tag1', tag_id=1)
        tag2 = TagCreator.create_tag(name='tag2', tag_id=2)

        CliPresenter.list_tags(tags=[tag, tag2])

        calls = [
            call(content=['Id', 'Tag'],
                 column_widths=self.column_widths, num_cols=self.num_cols),
            call(content=['1', 'tag1'],
                 column_widths=self.column_widths, num_cols=self.num_cols),
            call(content=['2', 'tag2'],
                 column_widths=self.column_widths, num_cols=self.num_cols),
        ]
        mock_format_table_row.assert_has_calls(calls)
