""" Retrieves relevant information from the database, calculates a per-tag
priority and passes the data on to the presenter.

Per-tag priority:
  - determines how urgently a certain topic (tag) should be reviewed
  - implemented as prio-score between 1 (high need to catch up) to 10 (no
    study necessary).

Priority algorithm:
The total tag priority is calculated as:

    prio = avg_weighted_problem_prio * experience

where:
  1) Avg. weighted problem prio
     Problems are rated in three categories: easy, medium, hard.
     The avg_weighted_prio is calculated as the weighted sum of the average
      priority of each of these categories.
     It is reasoned that:
       - easy problems signify the introduction of a topic
       - medium problems are more representative of actual
         topic knowledge as well as interview questions
       - hard problems are rather edge-cases or advanced interview
         questions --> not as essential as medium ones
     Therefore, the total average score for a tag is determined as:
     avg_score = 0.25 * avg_easy + 0.5 * avg_med + 0.25 * avg_hard
  2) Experience
    It does make sense to choose topics as fine-grained as possible.
    Per topic, a minimum of 5 questions is necessary to reach full
    'experience'. Hence:
        experience = max(1, num_problems/ 5)
"""

import numpy as np
import pandas as pd

from .get_problem import ProblemGetter
from .db_gateway_interface import DBGatewayInterface
from .presenter_interface import PresenterInterface
from spaced_repetition.domain.problem import Difficulty


class TagGetter:
    def __init__(self, db_gateway: DBGatewayInterface,
                 presenter: PresenterInterface):
        self.repo = db_gateway
        self.presenter = presenter

    def list_tags(self, sub_str: str = None):
        self.presenter.list_tags(
            tags=self.get_prioritized_tags(sub_str=sub_str))

    def get_prioritized_tags(self, sub_str: str = None) -> pd.DataFrame:
        tags = None
        if sub_str:
            tags = [tag.name for tag in self.repo.get_tags(sub_str=sub_str)]

        problem_getter = ProblemGetter(db_gateway=self.repo,
                                       presenter=self.presenter)
        problem_df = problem_getter.get_prioritized_problems(tags_must_have=tags)

        return self._prioritize_tags(problem_data=problem_df)

    @classmethod
    def _prioritize_tags(cls, problem_data: pd.DataFrame):
        if problem_data.empty:
            return pd.DataFrame()

        return problem_data \
            .groupby('tags') \
            .apply(cls._prioritize) \
            .reset_index() \
            .sort_values(['priority', 'KS (weighted avg)'])

    @classmethod
    def _prioritize(cls, group_df: pd.DataFrame) -> pd.Series:
        """ see docstring for description """
        if group_df.empty:
            return pd.Series(dtype='object')

        easy_avg_ks = cls._mean_knowledge_score(df=group_df,
                                                difficulty=Difficulty.EASY)
        med_avg_ks = cls._mean_knowledge_score(df=group_df,
                                               difficulty=Difficulty.MEDIUM)
        hard_avg_ks = cls._mean_knowledge_score(df=group_df,
                                                difficulty=Difficulty.HARD)

        weighted_ks = 0.25 * easy_avg_ks + 0.5 * med_avg_ks + 0.25 * hard_avg_ks
        experience = min(1.0, len(group_df) / 5)
        priority = weighted_ks * experience

        return pd.Series(
            data={
                'experience': experience,
                'KS (weighted avg)': weighted_ks,
                'priority': priority,
                'num_problems': len(group_df)},
            dtype='object')

    @staticmethod
    def _mean_knowledge_score(df: pd.DataFrame, difficulty: Difficulty):
        ks = df \
            .loc[df.difficulty == difficulty, 'KS'] \
            .mean()

        return ks if ks is not np.nan else 0
