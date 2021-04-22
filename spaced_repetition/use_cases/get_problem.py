import dataclasses
from typing import List

import pandas as pd

from spaced_repetition.domain.problem import Problem
from .db_gateway_interface import DBGatewayInterface
from .get_problem_log import ProblemLogGetter
from .helpers_pandas import add_missing_columns
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
        problem_df = self.get_prioritized_problems(name_substr=name_substr,
                                                   tags_any=tags_any,
                                                   tags_all=tags_all)

        problem_df.sort_values(by=sorted_by or 'KS',
                               inplace=True,
                               key=self._sort_key,
                               na_position='first')
        self.presenter.list_problems(problem_df)

    def show_problem_history(self, name: str):
        problems = self.repo.get_problems(name=name)
        if not problems:
            raise ValueError(f'Could not find problem with name "{name}"!')

        problem_log_df = self.plg.get_problem_logs(
            problem_ids=[problems[0].problem_id])
        self.presenter.show_problem_history(problem=problems[0],
                                            problem_log_info=problem_log_df)

    @staticmethod
    def _sort_key(col):
        """ case-insensitive sorting of text columns """
        if col.dtype == 'object':
            return col.str.lower()
        return col

    def list_problem_tag_combos(self, sorted_by: List[str] = None,
                                tag_substr: str = None):
        problems = self._get_problems()
        problems_denormalized = self._denormalize_problems(problems)
        knowledge_status = self.plg.get_knowledge_status()

        full_df = self._merge_problem_and_log_data(
            problem_data=problems_denormalized, log_data=knowledge_status)

        full_df.sort_values(by=sorted_by or 'KS',
                            inplace=True,
                            key=self._sort_key,
                            na_position='first')
        full_df = self._filter_tags(full_df, tag_substr=tag_substr)

        self.presenter.list_problem_tag_combos(full_df)

    @staticmethod
    def _denormalize_problems(problems: pd.DataFrame) -> pd.DataFrame:
        """ create a separate row per problem-tag combination """
        problems['tags'] = problems['tags'].str.split(', ')
        return problems \
            .explode('tags') \
            .rename(columns={'tags': 'tag'}) \
            .reset_index(drop=True)  # avoid identical idx in several rows

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

    def get_prioritized_problems(self, name_substr: str = None,
                                 tags_any: List[str] = None,
                                 tags_all: List[str] = None) -> pd.DataFrame:
        """ TODO: problem prio should be calculated from avg of
        corresponding problem-tag-combos """
        # problem_df = self._get_problems(name_substr=name_substr,
        #                                 tags_any=tags_any,
        #                                 tags_all=tags_all)
        #
        # problem_priorities = self.plg.get_problem_knowledge_scores(
        #     problem_ids=problem_df.problem_id.to_list())
        #
        # return problem_df.merge(problem_priorities,
        #                         on='problem_id',
        #                         how='outer',
        #                         validate='one_to_one')
        pass

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
        problem_row['tags'] = ', '.join(sorted(problem.tags))
        return problem_row
