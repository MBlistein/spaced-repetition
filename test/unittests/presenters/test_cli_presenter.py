import datetime as dt
import io
import unittest
from unittest.mock import patch

import pandas as pd
from pandas.testing import assert_frame_equal

from spaced_repetition.domain.problem import Difficulty, ProblemCreator
from spaced_repetition.domain.problem_log import Result
from spaced_repetition.presenters.cli_presenter import CliPresenter


PROBLEM = ProblemCreator.create(
    name='testname',
    difficulty=Difficulty(1),
    problem_id=1,
    tags=['test-tag'],
    url='test-url')


class TestCliPresenter(unittest.TestCase):
    def setUp(self):
        self.num_cols = 5
        self.column_widths = [5, 20, 20, 10, 25]

        self.problem_df = pd.DataFrame(data=[{
            'difficulty': Difficulty.MEDIUM,
            'ease': 2.5,
            'interval': 10,
            'KS': 2.0,
            'name': 'name',
            'problem_id': 5,
            'result': Result.NO_IDEA,
            'RF': 0.7,
            'surplus_col': 'not displayed',
            'tags': 'test-tag',
            'ts_logged': dt.datetime(2021, 1, 10, 8, 10, 0, 1561),
            'url': 'www.test.com'
        }])

    def test_problem_confirmation_txt(self):
        self.assertEqual("Created Problem 'testname' with id '1' "
                         "(difficulty 'EASY', tags: test-tag)",
                         CliPresenter._problem_confirmation_txt(problem=PROBLEM))

    def test_format_problem_df(self):
        intended_order = ['name', 'tags', 'difficulty', 'last_access',
                          'last_result', 'KS', 'RF', 'url', 'ease', 'interval']
        expected_df = pd.DataFrame(data=[{
            'difficulty': 'MEDIUM',
            'ease': 2.5,
            'interval': 10,
            'id': 5,
            'KS': 2.0,
            'last_access': '2021-01-10 08:10',
            'name': 'name',
            'last_result': Result.NO_IDEA.name,
            'RF': 0.7,
            'tags': 'test-tag',
            'url': 'www.test.com'}]) \
            .set_index('id') \
            .reindex(columns=intended_order)

        formatted_df = CliPresenter.format_problem_df(self.problem_df)

        assert_frame_equal(expected_df, formatted_df)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_list_problems(self, mock_stdout):
        # pep8: disable=line-too-long
        expected_output = \
            "|   id | name   | tags     | difficulty   | last_access      | last_result   |   KS |   RF | url          |   ease |   interval |\n" \
            "|------|--------|----------|--------------|------------------|---------------|------|------|--------------|--------|------------|\n" \
            "|    5 | name   | test-tag | MEDIUM       | 2021-01-10 08:10 | NO_IDEA       |    2 |  0.7 | www.test.com |    2.5 |         10 |\n"

        CliPresenter.list_problems(problems=self.problem_df)

        self.assertEqual(expected_output,
                         mock_stdout.getvalue())


# class TestCliPresenterTags(unittest.TestCase):
#     def setUp(self):
#         self.num_cols = 2
#         self.column_widths = [5, 10]
#
#     def test_format_tag_df(self):
#         test_df = pd.DataFrame(data=[
#             {'tags': 4,
#              'url': 'www',
#              'rank': 22,
#              'score': 1,
#              'difficulty': 2,
#              'name': 'name',
#              'ts_logged': dt.datetime(2021, 1, 10, 8, 10, 0, 1561),
#              'surplus_col': 'not displayed',
#              'problem_id': 5}])
#
#         formatted_df = CliPresenter.format_problem_df(test_df)
#
#         expected_df = pd.DataFrame(data=[
#             {'name': 'name',
#              'tags': 4,
#              'difficulty': 2,
#              'last_access': '2021-01-10 08:10',
#              'score': 1,
#              'rank': 22,
#              'url': 'www',
#              'id': 5}]) \
#             .set_index('id')
#
#         assert_frame_equal(formatted_df, expected_df)
#
#     @patch('sys.stdout', new_callable=io.StringIO)
#     def test_list_tags(self, mock_stdout):
#         test_df = pd.DataFrame(data=[{
#             'tags': 'test-tag',
#             'last_access': dt.datetime(2021, 1, 10, 15, 3, 5, 5151),
#             'difficulty': 'hard',
#             'name': 'name',
#             'url': 'www',
#             'rank': 1,
#             'score': 3,
#             'problem_id': 5}])
#
#         expected_output = \
#             "|   id | name   | tags     | difficulty   | last_access      |   score |   rank | url   |\n" \
#             "|------|--------|----------|--------------|------------------|---------|--------|-------|\n" \
#             "|    5 | name   | test-tag | hard         | 2021-01-10 15:03 |       3 |      1 | www   |\n"
#
#         CliPresenter.list_problems(problems=test_df)
#
#         self.assertEqual(expected_output,
#                          mock_stdout.getvalue())
