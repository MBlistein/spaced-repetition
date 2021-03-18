import datetime as dt
from math import exp, log
from typing import List

import pandas as pd
from dateutil.tz import gettz

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

        problem_df = pd.DataFrame(data=map(self.problem_to_row_content, problems))
        score_df = self.get_score_df(problem_ids=problem_df.problem_id.to_list())
        prio_df = self.get_prio_df(scored_logs=score_df)

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

    def get_score_df(self, problem_ids=None):
        problem_logs = self.get_problem_logs(problem_ids=problem_ids)
        score_df = self.add_scores(
            log_df=self.get_log_df(problem_logs=problem_logs))
        return self.last_score_per_problem(score_df=score_df) \
            .reset_index()

    @staticmethod
    def get_prio_df(scored_logs: pd.DataFrame,
                    ts: dt.datetime = dt.datetime.now(tz=gettz('UTC')))\
            -> pd.DataFrame:
        """Calculates the knowledge score KS per problem"""
        df = scored_logs.copy()

        def retention_score(df_row: pd.Series) -> float:
            days_since_last_study = (ts - df_row.ts_logged.to_pydatetime()).days
            days_over = days_since_last_study - df_row.interval
            return exp(log(1/2) * days_over / df_row.interval)

        df['RF'] = df.apply(retention_score, axis='columns')
        df['KS'] = df.RF * df.score
        return df

    def get_problem_logs(self, problem_ids: List[int] = None):
        return self.repo.get_problem_logs(problem_ids=problem_ids)

    @classmethod
    def get_log_df(cls, problem_logs: List[ProblemLog]) -> pd.DataFrame:
        return pd.DataFrame(data=map(cls.log_to_row_content, problem_logs))

    @staticmethod
    def log_to_row_content(log: ProblemLog) -> dict:
        return {'ease': log.ease,
                'problem_id': log.problem_id,
                'result': log.result.value,
                'interval': log.interval,
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

    def list_tags(self, sub_str: str = None):
        self.presenter.list_tags(
            tags=self.get_tag_df(sub_str=sub_str))

    def get_tag_df(self, sub_str: str = None) -> pd.DataFrame:
        problem_df = self.get_problem_df()

        if problem_df.empty:
            return problem_df

        return problem_df \
            .groupby('tags') \
            .apply(self.prioritize) \
            .reset_index() \
            .sort_values(['prio', 'avg_score']) \
            .set_index('prio')

    @classmethod
    def prioritize(cls, group_df: pd.DataFrame) -> pd.Series:
        """Determine how urgently a certain topic (tag) should be reviewed.
        Returns a prio-score between 1 (high need to catch up) to 10 (no
        study necessary).
          1) Avg. weighted problem prio
             Problems are rated in three categories: easy, medium, hard.
             The total avg_weighted_prio is calculated as the weighted
             sum of the avg_prio in each of these categories.
             It is reasoned that:
               - easy problems signify the introduction of a topic
               - medium problems are more representative of actual
                 topic knowledge as well as interview questions
               - hard problems are rather edge-cases or advanced interview
                 questions and therefore not as essential as medium ones
             Therefore, the total average score for a tag is determined as:
             avg_score = 0.25 * avg_easy + 0.5 * avg_med + 0.25 * avg_hard
          2) Experience
              It does make sense to choose topics as fine-grained as possible.
              Per topic, a minimum of 5 questions is necessary to reach full
              'experience'. The necessary experience per topic could be
              chosen individually in the future.
        """
        avg_score = group_df.score.mean()
        last_ts = group_df.ts_logged.max().to_pydatetime()
        num_problems = group_df.shape[0]

        now = dt.datetime.now(tz=gettz('UTC'))
        time_since_last_ts = now - last_ts
        prio = 1

        return pd.Series(data={
            'prio': prio,
            'avg_score': avg_score,
            'last_access': last_ts,
            'num_problems': num_problems,
        })
