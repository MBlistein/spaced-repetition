from typing import List

from spaced_repetition.domain.problem import (Difficulty,
                                              Problem,
                                              ProblemCreator)
from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface
from spaced_repetition.use_cases.presenter_interface import PresenterInterface
from .get_tag import TagGetter


class ProblemAdder:
    def __init__(self, db_gateway: DBGatewayInterface,
                 presenter: PresenterInterface):
        self.repo = db_gateway
        self.presenter = presenter

    def add_problem(self, name: str,
                    difficulty: Difficulty,
                    tags: List[str],
                    url: str = None):

        tag_getter = TagGetter(db_gateway=self.repo, presenter=self.presenter)
        problem = ProblemCreator.create(
            name=name,
            difficulty=difficulty,
            problem_id=None,
            tags=tag_getter.get_existing_tags(names=tags),
            url=url)

        self._assert_is_unique(problem=problem)
        created_problem = self.repo.create_problem(problem=problem)
        self.presenter.confirm_problem_created(problem=created_problem)

    def _assert_is_unique(self, problem: Problem):
        if self.repo.problem_exists(name=problem.name):
            raise ValueError(f"Problem name '{problem.name}' is not unique!")
