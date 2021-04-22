import dataclasses
import datetime as dt
from math import exp, log
from typing import List

import pandas as pd
from dateutil.tz import gettz

from spaced_repetition.domain.problem_log import ProblemLog
from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface
from spaced_repetition.use_cases.presenter_interface import PresenterInterface
from .helpers_pandas import add_missing_columns


RETENTION_FRACTION_PER_T = 0.5  # Fraction of remembered content after time T


class ProblemLogGetter:
    def __init__(self, db_gateway: DBGatewayInterface,
                 presenter: PresenterInterface):
        self.repo = db_gateway
        self.presenter = presenter

    def get_knowledge_status(self):
        """ Get the last recorded status per problem-log-combo """
        problem_log_data = self._last_entry_per_problem_tag_combo(
            plog_df=self._get_problem_log_data())

        return self._add_knowledge_scores(log_data=problem_log_data)

    @staticmethod
    def _last_entry_per_problem_tag_combo(plog_df: pd.DataFrame):
        columns = ['problem_id', 'tag', 'ts_logged', 'result', 'ease',
                   'interval']
        df = add_missing_columns(
            df=plog_df.loc[:, [col for col in columns if col in plog_df.columns]],
            required_columns=columns)

        return df \
            .sort_values('ts_logged') \
            .groupby(['problem_id', 'tag']) \
            .tail(1)

    def _get_problem_log_data(self) -> pd.DataFrame:
        problem_logs = self.repo.get_problem_logs()
        return pd.DataFrame(data=self._denormalize_logs(p_logs=problem_logs))

    @staticmethod
    def _denormalize_logs(p_logs: List[ProblemLog]) -> List[dict]:
        res = []
        for p_log in p_logs:
            for tag in p_log.tags:
                res.append({
                    'comment': p_log.comment,
                    'ease': p_log.ease,
                    'interval': p_log.interval,
                    'problem_id': p_log.problem_id,
                    'result': p_log.result,
                    'tag': tag.name,
                    'ts_logged': p_log.timestamp})
        return res

    def get_problem_logs(self, problem_ids: List[int] = None) -> pd.DataFrame:
        problem_logs = self.repo.get_problem_logs(problem_ids=problem_ids)
        return pd.DataFrame(data=map(self._log_to_row, problem_logs))

    @staticmethod
    def _log_to_row(p_log: ProblemLog) -> dict:
        row_content = dataclasses.asdict(p_log)
        row_content['ts_logged'] = row_content.pop('timestamp')
        row_content['tags'] = ', '.join(sorted([tag.name for tag in p_log.tags]))
        return row_content

    @classmethod
    def _add_knowledge_scores(
            cls, log_data: pd.DataFrame,
            ts: dt.datetime = dt.datetime.now(tz=gettz('UTC'))) -> pd.DataFrame:
        """Calculates the knowledge score 'KS' per log-entry (= log_data row)"""
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
