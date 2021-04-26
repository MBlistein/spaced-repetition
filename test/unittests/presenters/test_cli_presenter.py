import datetime as dt
import io
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal

from spaced_repetition.domain.problem import Difficulty, ProblemCreator
from spaced_repetition.domain.problem_log import ProblemLogCreator, Result
from spaced_repetition.domain.tag import TagCreator
from spaced_repetition.presenters.cli_presenter import CliPresenter


class TestCommonFormatters(unittest.TestCase):
    def test_format_difficulty(self):
        difficulty = pd.Series({1: Difficulty.MEDIUM})
        expected_res = pd.Series({1: Difficulty.MEDIUM.name})

        res = CliPresenter._format_difficulty(difficulty=difficulty)

        assert_series_equal(expected_res, res)

    def test_format_result(self):
        result = pd.Series({1: Result.KNEW_BY_HEART})
        expected_res = pd.Series({1: Result.KNEW_BY_HEART.name})

        res = CliPresenter._format_result(result=result)

        assert_series_equal(expected_res, res)

    def test_format_timestamp(self):
        timestamp = pd.Series({1: dt.datetime(2021, 1, 15, 10, 23, 45, 124)})
        expected_res = pd.Series({1: '2021-01-15 10:23'})

        res = CliPresenter._format_timestamp(ts=timestamp)

        assert_series_equal(expected_res, res)


class TestListProblemTagCombos(unittest.TestCase):
    def setUp(self):
        self.problem_tag_combo_df = pd.DataFrame(data=[{
            'difficulty': Difficulty.MEDIUM,
            'ease': 2.5,
            'interval': 10,
            'KS': 2.0,
            'problem': 'name',
            'problem_id': 5,
            'result': Result.NO_IDEA,
            'RF': 0.7,
            'surplus_col': 'not displayed',
            'tag': 'test-tag',
            'ts_logged': dt.datetime(2021, 1, 10, 8, 10, 0, 1561),
            'url': 'www.test.com'
        }])

        self.pre_format_cols = ['tag', 'problem', 'problem_id', 'difficulty', 'last_access',
                                'last_result', 'KS', 'RF', 'url', 'ease',
                                'interval']

        self.post_format_cols = ['problem', 'problem_id', 'difficulty', 'last_access',
                                 'last_result', 'KS', 'RF', 'url', 'ease',
                                 'interval']

    def test_format_df(self):
        expected_df = pd.DataFrame(data=[{
            'difficulty': 'MEDIUM',
            'ease': 2.5,
            'interval': 10,
            'problem_id': 5,
            'KS': 2.0,
            'last_access': '2021-01-10 08:10',
            'problem': 'name',
            'last_result': Result.NO_IDEA.name,
            'RF': 0.7,
            'tag': 'test-tag',
            'url': 'www.test.com'}]) \
            .set_index('tag') \
            .reindex(columns=self.post_format_cols)

        formatted_df = CliPresenter.format_df(
            self.problem_tag_combo_df,
            ordered_cols=self.pre_format_cols,
            index_col='tag')

        assert_frame_equal(expected_df, formatted_df)

    def test_format_problem_df_missing_cols(self):
        data_df = self.problem_tag_combo_df \
            .loc[:, ['problem', 'problem_id', 'ts_logged']] \
            .copy()

        expected_df = pd.DataFrame(data=[{
            'difficulty': np.nan,
            'ease': np.nan,
            'interval': np.nan,
            'problem_id': 5,
            'KS': np.nan,
            'last_access': '2021-01-10 08:10',
            'problem': 'name',
            'last_result': np.nan,
            'RF': np.nan,
            'tag': np.nan,
            'url': np.nan}]) \
            .set_index('tag') \
            .reindex(columns=self.post_format_cols)

        formatted_df = CliPresenter.format_df(data_df,
                                              ordered_cols=self.pre_format_cols,
                                              index_col='tag')

        assert_frame_equal(expected_df, formatted_df)

    def test_format_problem_df_empty_smoke_test(self):
        """ Too much trouble with getting the dtypes right; smoke test
        suffices for now """
        CliPresenter.format_df(pd.DataFrame(),
                               ordered_cols=self.pre_format_cols,
                               index_col='tag')

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_list_problem_tag_combos(self, mock_stdout):
        # pep8: disable=line-too-long
        expected_output = \
            "| tag      | problem   |   problem_id | difficulty   | last_access      | last_result   |   KS |   RF | url          |   ease |   interval |\n" \
            "|----------|-----------|--------------|--------------|------------------|---------------|------|------|--------------|--------|------------|\n" \
            "| test-tag | name      |            5 | MEDIUM       | 2021-01-10 08:10 | NO_IDEA       |    2 |  0.7 | www.test.com |    2.5 |         10 |\n"

        CliPresenter.list_problem_tag_combos(
            problem_tag_combos=self.problem_tag_combo_df)

        self.assertEqual(expected_output,
                         mock_stdout.getvalue())


class TestListProblems(unittest.TestCase):
    def setUp(self):
        self.problem_df = pd.DataFrame(data=[{
            'difficulty': Difficulty.MEDIUM,
            'ease': 2.5,
            'interval': 10,
            'KS': 2.0,
            'problem': 'test-prob',
            'problem_id': 5,
            'result': Result.NO_IDEA,
            'RF': 0.7,
            'surplus_col': 'not displayed',
            'tags': 'test-tag',
            'ts_logged': dt.datetime(2021, 1, 10, 8, 10, 0, 1561),
            'url': 'www.test.com'
        }])

        self.pre_format_cols = ['id', 'name', 'tags', 'difficulty', 'last_access',
                                'last_result', 'KS', 'RF', 'url', 'ease',
                                'interval']

        self.post_format_cols = ['name', 'tags', 'difficulty', 'last_access',
                                 'last_result', 'KS', 'RF', 'url', 'ease',
                                 'interval']

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_list_problems(self, mock_stdout):
        # pep8: disable=line-too-long
        expected_output = \
            "|   problem_id | problem   | tags     | difficulty   |   KS |   RF | url          |\n" \
            "|--------------|-----------|----------|--------------|------|------|--------------|\n" \
            "|            5 | test-prob | test-tag | MEDIUM       |    2 |  0.7 | www.test.com |\n"

        CliPresenter.list_problems(problems=self.problem_df)

        self.assertEqual(expected_output,
                         mock_stdout.getvalue())


class TestProblemHistory(unittest.TestCase):
    def setUp(self):
        self.problem = ProblemCreator.create(name='test_problem',
                                             difficulty=Difficulty.MEDIUM,
                                             tags=['test_tag'],
                                             problem_id=1)
        self.problem_log_info = pd.DataFrame(data=[{
            'comment': 'problem_log_1 comment',
            'problem_id': 1,
            'result': Result.NO_IDEA,
            'tags': 'tag_1',
            'ts_logged': dt.datetime(2021, 1, 10, 8, 10, 25, 1561),
        }])

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_show_problem_history(self, mock_stdout):
        expected_output = "History for problem 'test_problem':\n"
        expected_output += \
            "|    | ts_logged        | result   | comment               | tags   |\n" \
            "|----|------------------|----------|-----------------------|--------|\n" \
            "|  0 | 2021-01-10 08:10 | NO_IDEA  | problem_log_1 comment | tag_1  |\n"

        CliPresenter.show_problem_history(problem=self.problem,
                                          problem_log_info=self.problem_log_info)

        self.assertEqual(expected_output,
                         mock_stdout.getvalue())


class TestPresentTags(unittest.TestCase):
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
            columns=['tag', 'priority', 'KS (weighted avg)', 'experience',
                     'num_problems']) \
            .set_index('tag')

        assert_frame_equal(formatted_df, expected_df)

    def test_format_tag_df_empty(self):
        order = ['tag', 'priority', 'KS (weighted avg)', 'experience',
                 'num_problems']
        expected_res = pd.DataFrame(columns=order).set_index('tag')

        assert_frame_equal(expected_res,
                           CliPresenter.format_tag_df(pd.DataFrame()),
                           check_dtype=False, check_index_type=False)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_list_tags(self, mock_stdout):
        test_df = pd.DataFrame(
            data=[
                {'tag': 'test-tag',
                 'experience': 0.8,
                 'KS (weighted avg)': 5.0,
                 'priority': 4.0,
                 'num_problems': 4}])

        expected_output = \
            "| tag      |   priority |   KS (weighted avg) |   experience |   num_problems |\n" \
            "|----------|------------|---------------------|--------------|----------------|\n" \
            "| test-tag |          4 |                   5 |          0.8 |              4 |\n"

        CliPresenter.list_tags(tags=test_df)

        self.assertEqual(expected_output,
                         mock_stdout.getvalue())


class TestCliPresentConfirmations(unittest.TestCase):
    def setUp(self) -> None:
        self.problem = ProblemCreator.create(
            name='testname',
            difficulty=Difficulty(1),
            problem_id=1,
            tags=['test-tag'],
            url='test-url')

        self.problem_log = ProblemLogCreator.create(
            problem_id=1,
            result=Result.SOLVED_OPTIMALLY_IN_UNDER_25,
            tags=[TagCreator.create('test-tag')])

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
