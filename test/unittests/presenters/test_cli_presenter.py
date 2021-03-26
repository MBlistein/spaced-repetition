import datetime as dt
import io
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from spaced_repetition.domain.problem import Difficulty, ProblemCreator
from spaced_repetition.domain.problem_log import ProblemLogCreator, Result
from spaced_repetition.presenters.cli_presenter import CliPresenter


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

        self.intended_order = ['name', 'tags', 'difficulty', 'last_access',
                               'last_result', 'KS', 'RF', 'url', 'ease',
                               'interval']

    def test_format_problem_df(self):
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
            .reindex(columns=self.intended_order)

        formatted_df = CliPresenter.format_problem_df(self.problem_df)

        assert_frame_equal(expected_df, formatted_df)

    def test_format_problem_df_missing_cols(self):
        data_df = self.problem_df \
                      .loc[:, ['name', 'problem_id', 'ts_logged']] \
            .copy()

        expected_df = pd.DataFrame(data=[{
            'difficulty': np.nan,
            'ease': np.nan,
            'interval': np.nan,
            'id': 5,
            'KS': np.nan,
            'last_access': '2021-01-10 08:10',
            'name': 'name',
            'last_result': np.nan,
            'RF': np.nan,
            'tags': np.nan,
            'url': np.nan}]) \
            .set_index('id') \
            .reindex(columns=self.intended_order)

        formatted_df = CliPresenter.format_problem_df(data_df)

        assert_frame_equal(expected_df, formatted_df)

    def test_format_problem_df_empty_smoke_test(self):
        """ Too much trouble with getting the dtypes right; smoke test
        suffices for now """
        CliPresenter.format_problem_df(pd.DataFrame())

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


class TestCliPresenterTags(unittest.TestCase):
    def setUp(self):
        self.num_cols = 2
        self.column_widths = [5, 10]

    def test_format_tag_df(self):
        test_df = pd.DataFrame(data=[
            {'tags': 'test-tag',
             'experience': 0.8,
             'KS (weighted avg)': 5.0,
             'priority': 4.0,
             'num_problems': 4,
             'surplus_col': 'not displayed'}
        ])

        formatted_df = CliPresenter.format_tag_df(test_df)

        expected_df = pd.DataFrame(
            data=[
                {'tags': 'test-tag',
                 'experience': 0.8,
                 'KS (weighted avg)': 5.0,
                 'priority': 4.0,
                 'num_problems': 4}],
            columns=['tags', 'priority', 'KS (weighted avg)', 'experience',
                     'num_problems']) \
            .set_index('tags')

        assert_frame_equal(formatted_df, expected_df)

    def test_format_tag_df_empty(self):
        order = ['tags', 'priority', 'KS (weighted avg)', 'experience',
                 'num_problems']
        expected_res = pd.DataFrame(columns=order).set_index('tags')

        assert_frame_equal(expected_res,
                           CliPresenter.format_tag_df(pd.DataFrame()),
                           check_dtype=False, check_index_type=False)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_list_tags(self, mock_stdout):
        test_df = pd.DataFrame(
            data=[
                {'tags': 'test-tag',
                 'experience': 0.8,
                 'KS (weighted avg)': 5.0,
                 'priority': 4.0,
                 'num_problems': 4}])

        expected_output = \
            "| tags     |   priority |   KS (weighted avg) |   experience |   num_problems |\n" \
            "|----------|------------|---------------------|--------------|----------------|\n" \
            "| test-tag |          4 |                   5 |          0.8 |              4 |\n"

        CliPresenter.list_tags(tags=test_df)

        self.assertEqual(expected_output,
                         mock_stdout.getvalue())


class TestCliPresenterConfirmation(unittest.TestCase):
    def setUp(self) -> None:
        self.problem = ProblemCreator.create(
            name='testname',
            difficulty=Difficulty(1),
            problem_id=1,
            tags=['test-tag'],
            url='test-url')

        self.problem_log = ProblemLogCreator.create(
            problem_id=1, result=Result.SOLVED_OPTIMALLY_IN_UNDER_25)

    def test_problem_confirmation_txt(self):
        expected_txt = "Created Problem 'testname' with id '1' " \
                       "(difficulty 'EASY', tags: test-tag)"
        self.assertEqual(
            expected_txt,
            CliPresenter._problem_confirmation_txt(problem=self.problem))

    def test_problem_log_confirmation(self):
        expected_txt = \
            "Logged execution of Problem 'testname' with result " \
            "'SOLVED_OPTIMALLY_IN_UNDER_25' at "

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            CliPresenter.confirm_problem_logged(problem=self.problem,
                                                problem_log=self.problem_log)
            res = mock_stdout.getvalue()
            self.assertTrue(res.startswith(expected_txt))
