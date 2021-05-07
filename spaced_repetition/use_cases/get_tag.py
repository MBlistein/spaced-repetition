""" Retrieves relevant information from the database, calculates a per-tag
priority and passes the data on to the presenter.

Details on per-tag priority are described in the README"""

import dataclasses
from typing import List

import numpy as np
import pandas as pd

from spaced_repetition.domain.problem import Difficulty
from spaced_repetition.domain.tag import Tag
from .db_gateway_interface import DBGatewayInterface
from .get_problem import ProblemGetter
from .helpers_pandas import add_missing_columns, case_insensitive_sort
from .presenter_interface import PresenterInterface


class TagGetter:
    def __init__(self, db_gateway: DBGatewayInterface,
                 presenter: PresenterInterface):
        self.repo = db_gateway
        self.presenter = presenter

    def list_tags(self, sorted_by: List[str] = None, sub_str: str = None):
        tag_df = self._get_prioritized_tags(sub_str=sub_str)

        tag_df.sort_values(by=sorted_by or 'priority',
                           inplace=True,
                           key=case_insensitive_sort,
                           na_position='first')

        self.presenter.list_tags(tag_df)

    def get_existing_tags(self, names: List[str]) -> List[Tag]:
        """ Returns tags with the given names, and raises ValueError
        if at least one of them does not exist. """
        tags = self.repo.get_tags(names=names)

        if len(tags) < len(names):
            existing_tags = {tag.name for tag in tags}
            non_existing_tags = set(names).difference(existing_tags)
            raise ValueError("The following tag names don't exist: "
                             f"{non_existing_tags}")
        return tags

    def _get_prioritized_tags(self, sub_str: str = None) -> pd.DataFrame:
        tag_df = self._get_tags(sub_str=sub_str)

        problem_getter = ProblemGetter(db_gateway=self.repo,
                                       presenter=self.presenter)
        knowledge_status = problem_getter.get_knowledge_status()

        tag_data = self._merge_tag_and_knowledge_data(
            tag_data=tag_df, knowledge_data=knowledge_status)

        return self._prioritize_tags(tag_data=tag_data)

    @staticmethod
    def _merge_tag_and_knowledge_data(tag_data: pd.DataFrame,
                                      knowledge_data: pd.DataFrame) -> pd.DataFrame:
        return pd.merge(tag_data,
                        knowledge_data,
                        on='tag',
                        how='left')  # to allow filtering for specific tags

    def _get_tags(self, sub_str: str = None) -> pd.DataFrame:
        tags = self.repo.get_tags(sub_str=sub_str)

        tag_df = pd.DataFrame(data=[dataclasses.asdict(tag) for tag in tags]) \
            .rename(columns={'name': 'tag'})
        return add_missing_columns(tag_df,
                                   ['tag', 'tag_id'])

    @classmethod
    def _prioritize_tags(cls, tag_data: pd.DataFrame):
        if tag_data.empty:
            return add_missing_columns(
                df=pd.DataFrame(),
                required_columns=['experience', 'KW (weighted avg)',
                                  'num_problems', 'priority', 'tags'])
        return tag_data \
            .groupby('tag') \
            .apply(cls._prioritize) \
            .reset_index() \
            .sort_values(['priority', 'KS (weighted avg)'])

    @classmethod
    def _prioritize(cls, group_df: pd.DataFrame) -> pd.Series:
        easy_avg_ks = cls._mean_knowledge_score(df=group_df,
                                                difficulty=Difficulty.EASY)
        med_avg_ks = cls._mean_knowledge_score(df=group_df,
                                               difficulty=Difficulty.MEDIUM)
        hard_avg_ks = cls._mean_knowledge_score(df=group_df,
                                                difficulty=Difficulty.HARD)

        weighted_ks = max(0.5 * easy_avg_ks,
                          0.75 * med_avg_ks,
                          hard_avg_ks)
        experience = min(1.0, group_df.ts_logged.count() / 5)
        priority = weighted_ks * experience

        return pd.Series(
            data={
                'experience': experience,
                'KS (weighted avg)': weighted_ks,
                'num_problems': group_df.problem.count(),
                'priority': priority
            },
            dtype='object')

    @staticmethod
    def _mean_knowledge_score(df: pd.DataFrame, difficulty: Difficulty):
        # problems that have never been done should be ignored
        ks = df \
            .loc[df.difficulty == difficulty, 'KS'] \
            .mean()

        return ks if ks is not np.nan else 0
