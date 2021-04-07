""" Retrieves relevant information from the database, calculates a per-tag
priority and passes the data on to the presenter.

Details on per-tag priority are described in the README"""

import dataclasses
from typing import List

import numpy as np
import pandas as pd

from spaced_repetition.domain.problem import Difficulty
from .db_gateway_interface import DBGatewayInterface
from .get_problem import ProblemGetter
from .helpers_pandas import add_missing_columns
from .presenter_interface import PresenterInterface


class TagGetter:
    def __init__(self, db_gateway: DBGatewayInterface,
                 presenter: PresenterInterface):
        self.repo = db_gateway
        self.presenter = presenter

    def list_tags(self, sub_str: str = None):
        self.presenter.list_tags(
            tags=self._get_prioritized_tags(sub_str=sub_str))

    def _get_prioritized_tags(self, sub_str: str = None) -> pd.DataFrame:
        tag_df = self._get_tags(sub_str=sub_str)
        filter_tags = tag_df.tag.to_list() if sub_str else None

        problem_df = self._get_problems_per_tag(filter_tags=filter_tags)

        tag_data = pd.merge(tag_df, problem_df, on='tag', how='outer')

        return self._prioritize_tags(tag_data=tag_data)

    def _get_problems_per_tag(self, filter_tags: List[str] = None):
        problem_getter = ProblemGetter(db_gateway=self.repo,
                                       presenter=self.presenter)
        problem_df = problem_getter.get_prioritized_problems(
            tags_any=filter_tags)

        # de-normalize many-to-one relation between problems and tags
        if not problem_df.tags.empty:
            problem_df.tags = problem_df.tags.str.split(', ')
        problem_df = problem_df \
            .rename(columns={'tags': 'tag'}) \
            .explode('tag', ignore_index=True)

        return problem_df

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
        """ see docstring for description """
        if group_df.empty:
            raise ValueError("Handle group_df empty!")
        easy_avg_ks = cls._mean_knowledge_score(df=group_df,
                                                difficulty=Difficulty.EASY)
        med_avg_ks = cls._mean_knowledge_score(df=group_df,
                                               difficulty=Difficulty.MEDIUM)
        hard_avg_ks = cls._mean_knowledge_score(df=group_df,
                                                difficulty=Difficulty.HARD)

        weighted_ks = 0.25 * easy_avg_ks + 0.5 * med_avg_ks + 0.25 * hard_avg_ks
        # experience = min(1.0, len(group_df) / 5)
        experience = min(1.0, group_df.ts_logged.count() / 5)
        priority = weighted_ks * experience

        return pd.Series(
            data={
                'experience': experience,
                'KS (weighted avg)': weighted_ks,
                'num_problems': len(group_df),
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
