import datetime as dt
from math import exp, log
from typing import List

import pandas as pd
from dateutil.tz import gettz

from spaced_repetition.domain.problem import Problem
from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface
from spaced_repetition.use_cases.presenter_interface import PresenterInterface


class ProblemGetter:
    def __init__(self, db_gateway: DBGatewayInterface,
                 presenter: PresenterInterface):
        self.repo = db_gateway
        self.presenter = presenter

    def list_problems(self, name_substr: str = None,
                      sorted_by: List[str] = None,
                      tag_names: List[str] = None):
        self.presenter.list_problems(
            problems=self.get_problem_df(name_substr=name_substr,
                                         sorted_by=sorted_by,
                                         tag_names=tag_names))

    def get_problem_df(self, name_substr: str = None,
                       sorted_by: List[str] = None,
                       tag_names: List[str] = None) -> pd.DataFrame:
        problems = self.repo.get_problems(name_substr=name_substr,
                                          sorted_by=sorted_by,
                                          tag_names=tag_names)
        if not problems:
            return pd.DataFrame()

        problem_df = pd.DataFrame(data=map(self.problem_to_row_content,
                                           problems))
        problem_logs = self.get_log_df(problem_logs=self.get_problem_logs(
            problem_ids=problem_df.problem_id.to_list()))

        prio_df = self.get_prio_df(problem_logs=problem_logs)

        return problem_df.merge(prio_df,
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

    @staticmethod
    def get_prio_df(problem_logs: pd.DataFrame,
                    ts: dt.datetime = dt.datetime.now(tz=gettz('UTC')))\
            -> pd.DataFrame:
        """Calculates the knowledge score KS per problem"""
        df = problem_logs.copy()

        def retention_score(df_row: pd.Series) -> float:
            """Calulates the 'retention score', i.e. what percentage of
            knowledge is still remembered after a time period delta_t"""
            retention_fraction = 0.5  # after one period of length delta_t
            delta_t = df_row.interval

            days_since_last_study = (ts - df_row.ts_logged.to_pydatetime()).days
            days_over = days_since_last_study - df_row.interval

            return exp(log(retention_fraction) * days_over / delta_t)

        df['RF'] = df.apply(retention_score, axis='columns')
        df['KS'] = df.RF * df.score
        return df
