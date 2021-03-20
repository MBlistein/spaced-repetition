import dataclasses
from typing import List

import pandas as pd


from spaced_repetition.domain.problem_log import ProblemLog
from spaced_repetition.domain.score import SCORE_MAPPER
from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface
from spaced_repetition.use_cases.presenter_interface import PresenterInterface


class ProblemLogGetter:
    def __init__(self, db_gateway: DBGatewayInterface,
                 presenter: PresenterInterface):
        self.repo = db_gateway
        self.presenter = presenter

    def get_problem_logs(self, problem_ids: List[int] = None):
        problem_logs = self.repo.get_problem_logs(problem_ids=problem_ids)
        return pd.DataFrame(data=map(self._log_to_row_content, problem_logs))

    @staticmethod
    def _log_to_row_content(p_log: ProblemLog) -> dict:
        row_content = dataclasses.asdict(p_log)
        row_content['result'] = p_log.result.value
        row_content['ts_logged'] = row_content.pop('timestamp')
        return row_content

    def get_last_log_per_problem(self, problem_ids: List[int] = None):
        log_df = self.get_problem_logs(problem_ids=problem_ids)
        return self._last_log_per_problem(log_df)

    @staticmethod
    def _last_log_per_problem(log_df: pd.DataFrame):
        return log_df \
            .loc[:, ['problem_id', 'ts_logged', 'result', 'ease', 'interval']] \
            .sort_values('ts_logged') \
            .groupby('problem_id') \
            .tail(1) \
            .set_index('problem_id')

    @staticmethod
    def _add_scores(log_df: pd.DataFrame) -> pd.DataFrame:
        score_df = log_df.copy()
        score_df['score'] = score_df['result'].map(
            lambda x: SCORE_MAPPER[x].value)

        return score_df
