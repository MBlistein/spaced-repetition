import datetime as dt
import io
import unittest
from unittest.mock import call, patch

import pandas as pd
from pandas.testing import assert_frame_equal

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

    def test_format_problem_df(self):
        test_df = pd.DataFrame(data=[
            {'tags': 4,
             'url': 'www',
             'rank': 22,
             'score': 1,
             'difficulty': 2,
             'name': 'name',
             'ts_logged': dt.datetime(2021, 1, 10, 8, 10, 0, 1561),
             'surplus_col': 'not displayed',
             'problem_id': 5}])

        formatted_df = CliPresenter.format_problem_df(test_df)

        expected_df = pd.DataFrame(data=[
            {'name': 'name',
             'tags': 4,
             'difficulty': 2,
             'last_access': '2021-01-10 08:10',
             'score': 1,
             'rank': 22,
             'url': 'www',
             'id': 5}]) \
            .set_index('id')

        assert_frame_equal(formatted_df, expected_df)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_list_problems(self, mock_stdout):
        test_df = pd.DataFrame(data=[{
            'tags': 'test-tag',
            'last_access': dt.datetime(2021, 1, 10, 15, 3, 5, 5151),
            'difficulty': 'hard',
            'name': 'name',
            'url': 'www',
            'rank': 1,
            'score': 3,
            'problem_id': 5}])

        expected_output = \
            "|   id | name   | tags     | difficulty   | last_access      |   score |   rank | url   |\n" \
            "|------|--------|----------|--------------|------------------|---------|--------|-------|\n" \
            "|    5 | name   | test-tag | hard         | 2021-01-10 15:03 |       3 |      1 | www   |\n"

        CliPresenter.list_problems(problems=test_df)

        self.assertEqual(expected_output,
                         mock_stdout.getvalue())


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
