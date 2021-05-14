import dataclasses
from typing import List

import numpy as np
import pandas as pd

from spaced_repetition.domain.problem import Problem
from .db_gateway_interface import DBGatewayInterface
from .get_problem_log import ProblemLogGetter
from .helpers_pandas import add_missing_columns, denormalize_tags, case_insensitive_sort
from .presenter_interface import PresenterInterface


class ProblemGetter:
    def __init__(self, db_gateway: DBGatewayInterface,
                 presenter: PresenterInterface):
        self.presenter = presenter
        self.repo = db_gateway
        self.plg = ProblemLogGetter(db_gateway=self.repo,
                                    presenter=self.presenter)

    def list_problems(self, name_substr: str = None,
                      sorted_by: List[str] = None,
                      tags_any: List[str] = None,
                      tags_all: List[str] = None):
        knowledge_status = self.get_knowledge_status()
        problem_knowledge = self.aggregate_problems(knowledge_status)

        problems = self._get_problems(name_substr=name_substr,
                                      tags_all=tags_all,
                                      tags_any=tags_any)
        problem_df = pd.merge(
            problems,
            problem_knowledge,
            on='problem_id',
            how='left')  # allow filtering for specific problems

        problem_df.sort_values(by=sorted_by or 'KS',
                               inplace=True,
                               key=case_insensitive_sort,
                               na_position='first')
        self.presenter.list_problems(problem_df)

    @staticmethod
    def aggregate_problems(knowledge_status: pd.DataFrame) -> pd.DataFrame:
        relevant_data = knowledge_status \
            .loc[:, ['KS', 'problem_id', 'RF']] \

        # unlogged problems get KS = 0 because they should be studied
        relevant_data.KS.fillna(value=0, inplace=True)

        return relevant_data \
            .groupby('problem_id') \
            .agg({'KS': np.mean,
                  'RF': np.mean}) \
            .reset_index()

    def show_problem_history(self, name: str):
        problems = self.repo.get_problems(name=name)
        if not problems:
            raise ValueError(f'Could not find problem with name "{name}"!')

        problem_log_df = self.plg.get_problem_logs(
            problem_ids=[problems[0].problem_id])
        self.presenter.show_problem_history(problem=problems[0],
                                            problem_log_info=problem_log_df)

    def list_problem_tag_combos(self, sorted_by: List[str] = None,
                                tag_substr: str = None,
                                problem_substr: str = None):
        knowledge_status = self.get_knowledge_status()
        knowledge_status.sort_values(by=sorted_by or 'KS',
                                     inplace=True,
                                     key=case_insensitive_sort,
                                     na_position='first')
        df = self._filter_tags(df=knowledge_status, tag_substr=tag_substr)
        df = self._filter_problems(df=df, problem_substr=problem_substr)
        self.presenter.list_problem_tag_combos(df)

    def get_knowledge_status(self) -> pd.DataFrame:
        problems = self._get_problems()
        problems_denormalized = denormalize_tags(df=problems)
        knowledge_status = self.plg.get_last_log_per_problem_tag_combo()

        return self._merge_problem_and_log_data(
            problem_data=problems_denormalized, log_data=knowledge_status)

    @staticmethod
    def _merge_problem_and_log_data(problem_data: pd.DataFrame,
                                    log_data: pd.DataFrame) -> pd.DataFrame:
        return problem_data.merge(log_data,
                                  on=['problem_id', 'tag'],
                                  how='outer')

    @staticmethod
    def _filter_tags(df: pd.DataFrame, tag_substr: str):
        if tag_substr:
            df = df[df.tag.str.contains(tag_substr)]
        return df

    @staticmethod
    def _filter_problems(df: pd.DataFrame, problem_substr: str):
        if problem_substr:
            df = df[df.problem.str.contains(problem_substr)]
        return df

    def _get_problems(self, name_substr: str = None,
                      tags_any: List[str] = None,
                      tags_all: List[str] = None) -> pd.DataFrame:
        output_columns = ['difficulty', 'problem', 'problem_id', 'tags', 'url']
        problems = self.repo.get_problems(name_substr=name_substr,
                                          tags_any=tags_any,
                                          tags_all=tags_all)

        df = pd.DataFrame(data=map(self.problem_to_row_content, problems))
        return add_missing_columns(df, required_columns=output_columns)

    @staticmethod
    def problem_to_row_content(problem: Problem) -> dict:
        problem_row = dataclasses.asdict(problem)
        problem_row['problem'] = problem_row.pop('name')
        problem_row['tags'] = ', '.join(sorted([t.name for t in problem.tags]))
        return problem_row
