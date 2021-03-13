import datetime as dt
import unittest
from unittest.mock import Mock, patch

import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal

from spaced_repetition.domain.problem import Difficulty, ProblemCreator
from spaced_repetition.domain.problem_log import ProblemLog, Result
from spaced_repetition.domain.score import Score
from spaced_repetition.use_cases.get_problem import ProblemGetter


class TestGetProblems(unittest.TestCase):
    def setUp(self):
        self.p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())
        self.p_g.repo.get_problems.return_value = 'problems_from_repo'
        self.p_g.presenter = Mock()

    @patch.object(ProblemGetter, attribute='get_problem_df')
    def test_get_problem_null_args(self, mock_get_problem_df):
        mock_get_problem_df.return_value = 'problem_df'

        self.p_g.list_problems()

        # noinspection PyUnresolvedReferences
        self.p_g.repo.get_problems.assert_called_once_with(
            name_substr=None, sorted_by=None, tags=None)

        mock_get_problem_df.assert_called_once_with(
            problems='problems_from_repo')

        # noinspection PyUnresolvedReferences
        self.p_g.presenter.list_problems.assert_called_once_with(
            problems='problem_df')

    @patch.object(ProblemGetter, attribute='get_problem_df')
    def test_get_problem_full_args(self, mock_get_problem_df):
        mock_get_problem_df.return_value = 'problem_df'

        self.p_g.list_problems(name_substr='subs',
                               sorted_by=['arg1', 'arg2'],
                               tags=['tag1', 'tag2'])

        # noinspection PyUnresolvedReferences
        self.p_g.repo.get_problems.assert_called_once_with(
            name_substr='subs',
            sorted_by=['arg1', 'arg2'],
            tags=['tag1', 'tag2'])

        mock_get_problem_df.assert_called_once_with(
            problems='problems_from_repo')

        # noinspection PyUnresolvedReferences
        self.p_g.presenter.list_problems.assert_called_once_with(
            problems='problem_df')


class TestGetProblemLogs(unittest.TestCase):
    def setUp(self):
        self.p_g = ProblemGetter(db_gateway=Mock(), presenter=Mock())
        self.p_g.presenter = Mock()

    def test_get_all_problem_logs(self):
        self.p_g.get_problem_logs()

        # noinspection PyUnresolvedReferences
        self.p_g.repo.get_problem_logs.assert_called_once_with(
            problem_ids=None)

    def test_get_problem_logs(self):
        self.p_g.get_problem_logs(problem_ids=[1, 2])

        # noinspection PyUnresolvedReferences
        self.p_g.repo.get_problem_logs.assert_called_once_with(
            problem_ids=[1, 2])


class TestGetProblemDF(unittest.TestCase):
    def setUp(self):
        mock_gateway = Mock()
        mock_gateway.get_problem_logs.return_value = [
            ProblemLog(problem_id=3,
                       result=Result.NO_IDEA,
                       timestamp=dt.datetime(2021, 1, 5, 10))]

        self.p_g = ProblemGetter(db_gateway=mock_gateway, presenter=Mock())
        self.problem = ProblemCreator.create_problem(
            name='testname',
            difficulty=Difficulty(1),
            problem_id=3,
            tags=['test-tag'],
            url='test-url')

    def test_get_problem_df(self):
        expected_df = pd.DataFrame(data=[{'name': 'testname',
                                          'problem_id': 3,
                                          'difficulty': 'EASY',
                                          'tags': 'test-tag',
                                          'url': 'test-url',
                                          'ts_logged': dt.datetime(2021, 1, 5, 10),
                                          'score': Score.BAD.value}])

        assert_frame_equal(self.p_g.get_problem_df(problems=[self.problem]),
                           expected_df)

    def test_format_problem_to_row_content(self):
        expected_res = {'name': self.problem.name,
                        'problem_id': self.problem.problem_id,
                        'difficulty': self.problem.difficulty.name,
                        'tags': ', '.join(sorted(self.problem.tags)),
                        'url': self.problem.url}
        self.assertEqual(self.p_g.problem_to_row_content(problem=self.problem),
                         expected_res)

    def test_get_log_df(self):
        time_1 = dt.datetime(2021, 1, 10, 1)
        time_2 = dt.datetime(2021, 1, 10, 5)
        problem_logs = [
            ProblemLog(problem_id=1,
                       result=Result.NO_IDEA,
                       timestamp=time_1),
            ProblemLog(problem_id=2,
                       result=Result.SOLVED_OPTIMALLY_SLOWER,
                       timestamp=time_2)]

        expected_res = pd.DataFrame([
            {'problem_id': 1,
             'result': Result.NO_IDEA.value,
             'ts_logged': time_1},
            {'problem_id': 2,
             'result': Result.SOLVED_OPTIMALLY_SLOWER.value,
             'ts_logged': time_2}])

        assert_frame_equal(self.p_g.get_log_df(problem_logs=problem_logs),
                           expected_res)

    def test_format_log_to_df_row(self):
        time_1 = dt.datetime(2021, 1, 10, 1)
        problem_log = ProblemLog(problem_id=1,
                                 result=Result.NO_IDEA,
                                 timestamp=time_1)

        expected_res = {'problem_id': problem_log.problem_id,
                        'result': problem_log.result.value,
                        'ts_logged': problem_log.timestamp}
        self.assertEqual(self.p_g.log_to_row_content(log=problem_log),
                         expected_res)

    def test_add_scores(self):
        time_1 = dt.datetime(2021, 3, 8, 10, 1)

        log_df = pd.DataFrame(data=[
            {'problem_id': 1,
             'ts_logged': time_1,
             'result': Result.SOLVED_OPTIMALLY_SLOWER.value}
        ])

        expected_df = pd.DataFrame(data=[
            {'problem_id': 1,
             'ts_logged': time_1,
             'result': Result.SOLVED_OPTIMALLY_SLOWER.value,
             'score': Score.MEDIUM.value}
        ])

        assert_frame_equal(self.p_g.add_scores(log_df=log_df),
                           expected_df)

    def test_last_score_per_problem(self):
        score_df = pd.DataFrame(data=[
            {'problem_id': 1, 'ts_logged': dt.datetime(2021, 1, 1, 8), 'other_col': 'some_val', 'score': 1},
            {'problem_id': 1, 'ts_logged': dt.datetime(2021, 1, 1, 9), 'other_col': 'some_val', 'score': 3},
            {'problem_id': 2, 'ts_logged': dt.datetime(2021, 1, 1, 15), 'other_col': 'some_val', 'score': 4},
            {'problem_id': 2, 'ts_logged': dt.datetime(2021, 1, 1, 7), 'other_col': 'some_val', 'score': 2}
        ])

        expected_df = pd.DataFrame(data=[
            {'problem_id': 1, 'ts_logged': dt.datetime(2021, 1, 1, 9), 'score': 3},
            {'problem_id': 2, 'ts_logged': dt.datetime(2021, 1, 1, 15), 'score': 4}]) \
            .set_index('problem_id')

        # set_index to problem_id to avoid differing row indices
        assert_frame_equal(self.p_g.last_score_per_problem(score_df=score_df),
                           expected_df)
