import dataclasses
import datetime as dt
from math import exp, log
from typing import List

import pandas as pd
from dateutil.tz import gettz

from spaced_repetition.domain.problem_log import ProblemLog, Result
from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface
from spaced_repetition.use_cases.presenter_interface import PresenterInterface
from .helpers_pandas import add_missing_columns, denormalize_tags


RETENTION_FRACTION_PER_T = 0.5  # Fraction of remembered content after time T


class ProblemLogGetter:
    def __init__(self, db_gateway: DBGatewayInterface,
                 presenter: PresenterInterface):
        self.repo = db_gateway
        self.presenter = presenter

    def get_last_log_per_problem_tag_combo(self) -> pd.DataFrame:
        """ Get the last recorded status per problem-log-combo """
        problem_log_data = self._get_problem_log_data()

        return self._add_knowledge_scores(
            log_data=self._last_entry_per_problem_tag_combo(problem_log_data))

    @staticmethod
    def _last_entry_per_problem_tag_combo(plog_df: pd.DataFrame) -> pd.DataFrame:
        columns = ['problem_id', 'tag', 'ts_logged', 'result', 'ease',
                   'interval']
        df = add_missing_columns(
            df=plog_df.loc[:, [col for col in columns if col in plog_df.columns]],
            required_columns=columns)

        return df \
            .sort_values('ts_logged') \
            .groupby(['problem_id', 'tag']) \
            .tail(1)

    def get_problem_logs(self, problem_ids: List[int] = None) -> pd.DataFrame:
        problem_logs = self.repo.get_problem_logs(problem_ids=problem_ids)
        df = pd.DataFrame(data=map(self._log_to_row, problem_logs))

        return add_missing_columns(df, required_columns=[
            'problem_id', 'result', 'tags', 'comment', 'ts_logged'])

    def _get_problem_log_data(self) -> pd.DataFrame:
        log_df = self.get_problem_logs()
        problem_tag_combo_df = denormalize_tags(df=log_df)
        return SuperMemo2.add_spacing_data(log_data=problem_tag_combo_df)

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


class SuperMemo2:
    """ Applies a (modified, see docs) SM2 algorithm to the problem log data,
    to schedule repetition dates for efficient study.
    Implemented via Event Sourcing to:
     * log multiple tags with the same ProblemLog
     * be able to adapt SM2 in the future without touching the database."""

    DEFAULT_EASE = 2.5
    EASE_DELTA = 0.12
    INTERVAL_KNEW_BY_HEART = 21
    INTERVAL_SOLVED_OPTIMALLY_IN_UNDER_25 = 14
    INTERVAL_SOLVED_OPTIMALLY_SLOWER = 7
    INTERVAL_NON_OPTIMAL_SOLUTION = 3
    MINIMUM_EASE = 1.3

    INITIAL_INTERVALS = {
        Result.KNEW_BY_HEART: INTERVAL_KNEW_BY_HEART,
        Result.SOLVED_OPTIMALLY_SLOWER: INTERVAL_SOLVED_OPTIMALLY_SLOWER,
        Result.SOLVED_OPTIMALLY_IN_UNDER_25: INTERVAL_SOLVED_OPTIMALLY_IN_UNDER_25}

    @classmethod
    def add_spacing_data(cls, log_data: pd.DataFrame) -> pd.DataFrame:
        """ The log_data DataFrame needs a column 'result' of type Result"""
        return log_data \
            .groupby(['problem_id', 'tag']) \
            .apply(cls._add_spacing_data)

    @classmethod
    def _add_spacing_data(cls, group_df: pd.DataFrame) -> pd.DataFrame:
        group_df.sort_values('ts_logged', inplace=True)
        group_df_with_ease = cls._add_ease(group_df=group_df)
        return cls._add_interval(group_df=group_df_with_ease)

    @classmethod
    def _add_ease(cls, group_df: pd.DataFrame) -> pd.DataFrame:
        """Part of 'SuperMemo2': evolve the factor with which spacing interval
        is grown upon successful problem completion: the ease.
        Concretely:
          * start with the default ease
          * optimal result achieved without hint --> evolve ease
          * optimal result not achieved (without help) --> back to default
          * never fall under a certain minimum ease
        """
        group_df['ease'] = cls.DEFAULT_EASE

        for idx in range(1, len(group_df)):
            ease = cls.DEFAULT_EASE
            prev_ease = group_df.ease.iloc[idx-1]
            if group_df.result.iloc[idx] == Result.KNEW_BY_HEART:
                ease = prev_ease + cls.EASE_DELTA
            elif group_df.result.iloc[idx] == Result.SOLVED_OPTIMALLY_IN_UNDER_25:
                ease = prev_ease
            elif group_df.result.iloc[idx] == Result.SOLVED_OPTIMALLY_SLOWER:
                ease = max(prev_ease - cls.EASE_DELTA, cls.MINIMUM_EASE)

            group_df.iloc[idx, group_df.columns.get_loc('ease')] = ease
        return group_df

    @classmethod
    def _add_interval(cls, group_df: pd.DataFrame) -> pd.DataFrame:
        """Part of 'SuperMemo2': If a problem was solved optimally, the spacing
        interval gets multiplied by the ease to determine the next repetition.
        Else: the interval gets reset to a default."""
        group_df['interval'] = 0

        # initial attempt
        group_df.iloc[0, group_df.columns.get_loc('interval')] = \
            cls.INITIAL_INTERVALS.get(group_df.result.iloc[0],
                                      cls.INTERVAL_NON_OPTIMAL_SOLUTION)

        # follow-up attempts
        for idx in range(1, len(group_df)):
            if group_df.result.iloc[idx].value >= Result.SOLVED_OPTIMALLY_SLOWER.value:
                # eventually reached the optimal result without help
                group_df.iloc[idx, group_df.columns.get_loc('interval')] = \
                    round(group_df.ease.iloc[idx] * group_df.interval.iloc[idx-1])
            else:
                # did not find the optimal solution (without hint) -> start over
                group_df.iloc[idx, group_df.columns.get_loc('interval')] = \
                    cls.INTERVAL_NON_OPTIMAL_SOLUTION

        return group_df
