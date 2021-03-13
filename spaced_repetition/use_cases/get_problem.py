import datetime as dt
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

    def list_tags(self, sub_str: str = None):
        self.presenter.list_tags(
            tags=self.get_tag_df(sub_str=sub_str))

    def get_tag_df(self, sub_str: str = None) -> pd.DataFrame:
        problem_df = self.get_problem_df()
        return problem_df \
            .groupby('tags') \
            .apply(self.prioritize) \
            .reset_index() \
            .sort_values(['prio', 'avg_score']) \
            .set_index('prio')

    @classmethod
    def prioritize(cls, group_df: pd.DataFrame) -> pd.Series:
        """Determine how urgently a certain topic (tag) should be reviewed.
        Determine a prio-score between 1 (high need to catch up) to 10 (no
        further study necessary).
        Ideas:
            * a high avg_score with high experience (solved many problems)
              means high confidence on the topic --> low prio
            * a high avg_score with little experience may not mean much, further
              experience is required --> medium prio
            * if the last time that the topic was studied has been a long time
              ago, it should also be refreshed --> medium prio
            * an unstudied topic should be started asap, but not as urgently
              as a currently bad topic should be reviewed
            * a topic with a bad avg score should be reviewed asap --> there is
              a known deficiency. However, it should not constantly be at the
              top to make room for other topics as well
            * a problem's difficulty should also be taken into account; a topic
              with good scores on hard problems should be rated less urgent
              that a topic with very good scores on medium problems.
            """
        avg_score = group_df.score.mean()
        last_ts = group_df.ts_logged.max().to_pydatetime()
        num_problems = group_df.shape[0]

        now = dt.datetime.now(tz=gettz('UTC'))
        time_since_last_ts = now - last_ts

        return pd.Series(data={
            'prio': cls.prioritize(avg_score=avg_score,
                                         num_problems=num_problems,
                                         last_ts=last_ts),
            'avg_score': avg_score,
            'last_access': last_ts,
            'num_problems': num_problems,
        })

