from typing import Callable, List, Union

import pandas as pd
import numpy as np

from spaced_repetition.domain.problem import Problem
from spaced_repetition.domain.problem_log import ProblemLog
from spaced_repetition.domain.score import SCORE_MAPPER
from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface
from spaced_repetition.use_cases.presenter_interface import PresenterInterface


class ProblemGetter:
    def __init__(self, db_gateway: DBGatewayInterface,
                 presenter: PresenterInterface):
        self.repo = db_gateway
        self.presenter = presenter

    def list_problems(self, name_substr: str = None,
                      sorted_by: List[str] = None,
                      tags: List[str] = None):
        self.presenter.list_problems(
            problems=self.get_problem_df(
                problems=self.repo.get_problems(name_substr=name_substr,
                                                sorted_by=sorted_by,
                                                tags=tags)))

    def get_problem_df(self, problems: List[Problem]) -> pd.DataFrame:
        problem_df = pd.DataFrame(data=map(self.problem_to_row_content, problems))
        score_df = self.get_score_df(problem_ids=problem_df.problem_id.to_list())

        return problem_df.merge(score_df,
                                on='problem_id',
                                how='outer',
                                validate='one_to_one')

    @staticmethod
    def problem_to_row_content(problem: Problem) -> dict:
        return {'name': problem.name,
                'problem_id': problem.problem_id,
                'difficulty': problem.difficulty.name,
                'tags': ', '.join(sorted(problem.tags)),
                'url': problem.url}

    def get_score_df(self, problem_ids=None):
        problem_logs = self.get_problem_logs(problem_ids=problem_ids)
        score_df = self.add_scores(
            log_df=self.get_log_df(problem_logs=problem_logs))
        return self.last_score_per_problem(score_df=score_df) \
            .reset_index()

    def get_problem_logs(self, problem_ids: List[int] = None):
        return self.repo.get_problem_logs(problem_ids=problem_ids)

    @classmethod
    def get_log_df(cls, problem_logs: List[ProblemLog]) -> pd.DataFrame:
        return pd.DataFrame(data=map(cls.log_to_row_content, problem_logs))

    @staticmethod
    def log_to_row_content(log: ProblemLog) -> dict:
        return {'problem_id': log.problem_id,
                'result': log.result.value,
                'ts_logged': log.timestamp}

    @staticmethod
    def add_scores(log_df: pd.DataFrame) -> pd.DataFrame:
        score_df = log_df.copy()
        score_df['score'] = score_df['result'].map(
            lambda x: SCORE_MAPPER[x].value)

        return score_df

    @staticmethod
    def last_score_per_problem(score_df: pd.DataFrame):
        """Needs a dataframe with (at least) columns: 'problem_id', 'score'.
        Returns a dataframe with 'score' aggregated by 'problem_id."""
        return score_df \
            .loc[:, ['problem_id', 'ts_logged', 'score']] \
            .sort_values('ts_logged') \
            .groupby('problem_id') \
            .tail(1) \
            .set_index('problem_id')
