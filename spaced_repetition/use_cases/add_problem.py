from typing import List

from spaced_repetition.domain.problem import (Difficulty,
                                              Problem,
                                              ProblemCreator)
from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface
from spaced_repetition.use_cases.presenter_interface import PresenterInterface


class ProblemAdder:
    def __init__(self, db_gateway: DBGatewayInterface,
                 presenter: PresenterInterface):
        self.repo = db_gateway
        self.presenter = presenter

    def add_problem(self, name: str,
                    difficulty: Difficulty,
                    tags: List[str],
                    url: str = None):
        problem = ProblemCreator.create_problem(
            name=name,
            difficulty=difficulty,
            tags=tags,
            url=url)

        self._assert_is_unique(problem=problem)
        self.repo.create_problem(problem=problem)
        self.presenter.confirm_problem_created(problem=problem)

    def _assert_is_unique(self, problem: Problem):
        if len(self.repo.get_problems(name=problem.name)) > 0:
            raise ValueError(f"Problem name '{problem.name}' is not unique!")
