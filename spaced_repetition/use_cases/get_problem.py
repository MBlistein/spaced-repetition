import dataclasses
from typing import List

import pandas as pd

from spaced_repetition.domain.problem import Problem
from .db_gateway_interface import DBGatewayInterface
from .get_problem_log import ProblemLogGetter
from .presenter_interface import PresenterInterface


class ProblemGetter:
    def __init__(self, db_gateway: DBGatewayInterface,
                 presenter: PresenterInterface):
        self.presenter = presenter
        self.repo = db_gateway

    def list_problems(self, name_substr: str = None,
                      sorted_by: List[str] = None,
                      tags_must_have: List[str] = None):
        self.presenter.list_problems(
            problems=self.get_prioritized_problems(name_substr=name_substr,
                                                   sorted_by=sorted_by,
                                                   tags_must_have=tags_must_have))

    def get_prioritized_problems(self, name_substr: str = None,
                                 sorted_by: List[str] = None,
                                 tags_must_have: List[str] = None) -> pd.DataFrame:
        problem_df = self.get_problems(name_substr=name_substr,
                                       tags_must_have=tags_must_have)
        if problem_df.empty:
            return pd.DataFrame()

        plg = ProblemLogGetter(db_gateway=self.repo, presenter=self.presenter)
        problem_priorities = plg.get_problem_knowledge_scores(
            problem_ids=problem_df.problem_id.to_list())

        return problem_df.merge(problem_priorities,
                                on='problem_id',
                                how='outer',
                                validate='one_to_one')

    def get_problems(self, name_substr: str = None,
                     tags_must_have: List[str] = None) -> pd.DataFrame:
        problems = self.repo.get_problems(name_substr=name_substr,
                                          tags_must_have=tags_must_have)
        return pd.DataFrame(data=map(self.problem_to_row_content, problems))

    @staticmethod
    def problem_to_row_content(problem: Problem) -> dict:
        problem_row = dataclasses.asdict(problem)
        problem_row['tags'] = ', '.join(sorted(problem.tags))
        return problem_row
