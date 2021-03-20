"""


NONFUNCTIONAL WIP


"""

import datetime as dt

import pandas as pd
from dateutil.tz import gettz

from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface
from spaced_repetition.use_cases.presenter_interface import PresenterInterface


class TagGetter:
    def __init__(self, db_gateway: DBGatewayInterface,
                 presenter: PresenterInterface):
        self.repo = db_gateway
        self.presenter = presenter

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
