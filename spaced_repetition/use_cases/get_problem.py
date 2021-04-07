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

    @staticmethod
    def _sort_key(col):
        """ case-insensitive sorting of text columns """
        if col.dtype == 'object':
            return col.str.lower()
        return col

    def get_prioritized_problems(self, name_substr: str = None,
                                 tags_any: List[str] = None,
                                 tags_all: List[str] = None) -> pd.DataFrame:
        problem_df = self._get_problems(name_substr=name_substr,
                                        tags_any=tags_any,
                                        tags_all=tags_all)

        plg = ProblemLogGetter(db_gateway=self.repo, presenter=self.presenter)
        problem_priorities = plg.get_problem_knowledge_scores(
            problem_ids=problem_df.problem_id.to_list())

        return problem_df.merge(problem_priorities,
                                on='problem_id',
                                how='outer',
                                validate='one_to_one')

    def _get_problems(self, name_substr: str = None,
                      tags_any: List[str] = None,
                      tags_all: List[str] = None) -> pd.DataFrame:
        output_columns = ['difficulty', 'name', 'problem_id', 'tags', 'url']
        problems = self.repo.get_problems(name_substr=name_substr,
                                          tags_any=tags_any,
                                          tags_all=tags_all)

        df = pd.DataFrame(data=map(self.problem_to_row_content, problems))
        return add_missing_columns(df, required_columns=output_columns)

    @staticmethod
    def problem_to_row_content(problem: Problem) -> dict:
        problem_row = dataclasses.asdict(problem)
        problem_row['tags'] = ', '.join(sorted(problem.tags))
        return problem_row
