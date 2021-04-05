import dataclasses
import datetime as dt
from math import exp, log
from typing import List

import pandas as pd
from dateutil.tz import gettz

from spaced_repetition.domain.problem_log import ProblemLog
from spaced_repetition.domain.score import SCORE_MAPPER
from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface
from spaced_repetition.use_cases.presenter_interface import PresenterInterface
from .helpers_pandas import add_missing_columns


RETENTION_FRACTION_PER_T = 0.5  # Fraction of remembered content after time T


class ProblemLogGetter:
    def __init__(self, db_gateway: DBGatewayInterface,
                 presenter: PresenterInterface):
        self.repo = db_gateway
        self.presenter = presenter

    def get_problem_knowledge_scores(self, problem_ids: List[int] = None):
        return self._get_knowledge_scores(
            log_data=self._get_last_log_per_problem(problem_ids=problem_ids))

    def _get_problem_logs(self, problem_ids: List[int] = None) -> pd.DataFrame:
        problem_logs = self.repo.get_problem_logs(problem_ids=problem_ids)
        return pd.DataFrame(data=map(self._log_to_row_content, problem_logs))

    @staticmethod
    def _log_to_row_content(p_log: ProblemLog) -> dict:
        row_content = dataclasses.asdict(p_log)
        row_content['ts_logged'] = row_content.pop('timestamp')
        return row_content

    def _get_last_log_per_problem(self, problem_ids: List[int] = None):
        log_df = self._get_problem_logs(problem_ids=problem_ids)
        return self._last_log_per_problem(log_df)

    @staticmethod
    def _last_log_per_problem(log_df: pd.DataFrame):
        columns = ['problem_id', 'ts_logged', 'result', 'ease', 'interval']

        return add_missing_columns(
            df=log_df.loc[:, [col for col in columns if col in log_df.columns]],
            required_columns=columns) \
            .sort_values('ts_logged') \
            .groupby('problem_id') \
            .tail(1)

    @staticmethod
    def _add_scores(log_df: pd.DataFrame) -> pd.DataFrame:
        score_df = log_df.copy()
        score_df['score'] = score_df['result'].map(
            lambda x: SCORE_MAPPER[x].value)

        return score_df

    @classmethod
    def _get_knowledge_scores(
            cls, log_data: pd.DataFrame,
            ts: dt.datetime = dt.datetime.now(tz=gettz('UTC'))) -> pd.DataFrame:
        """Calculates the knowledge score 'KS' per problem"""
        df = log_data.copy()

        if df.empty:
            return add_missing_columns(df, required_columns=['KS', 'RF'])

        df['RF'] = df.apply(cls._retention_score,  # noqa --> pycharm bug, remove noqa in v2021.1
                            axis='columns',
                            args=(ts,))
        df['KS'] = df.RF * df.result.map(lambda x: x.value)
        return df

    @staticmethod
    def _retention_score(df_row: pd.Series, ts: dt.datetime) -> float:
        """Calculates the 'retention score' 0 <= RF <= 1,
        the percentage of knowledge retained at time ts"""
        days_since_last_study = (ts - df_row.ts_logged.to_pydatetime()) \
            .total_seconds() \
            / 3600 / 24

        # negative days_over would make RF > 1
        days_over = max(0, days_since_last_study - df_row.interval)

        return exp(log(RETENTION_FRACTION_PER_T) * days_over / df_row.interval)
