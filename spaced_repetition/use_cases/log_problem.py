from typing import List, Union

from spaced_repetition.domain.problem_log import (ProblemLog, ProblemLogCreator,
                                                  Result)
from .db_gateway_interface import DBGatewayInterface
from .get_tag import TagGetter
from .presenter_interface import PresenterInterface


class ProblemLogger:
    def __init__(self, db_gateway: DBGatewayInterface,
                 presenter: PresenterInterface):
        self.repo = db_gateway
        self.presenter = presenter

    def log_problem(self, comment: str, problem_name: str, result: Result,
                    tags: List[str]):
        try:
            problem = self.repo.get_problems(name=problem_name)[0]
        except IndexError:
            raise ValueError(
                f"Problem with name '{problem_name}' does not exist, "
                "try searching for similar problems.")

        tag_getter = TagGetter(db_gateway=self.repo, presenter=self.presenter)

        problem_log = ProblemLogCreator.create(
            comment=comment,
            problem_id=problem.problem_id,
            result=result,
            tags=tag_getter.get_existing_tags(names=tags))

        self.repo.create_problem_log(problem_log=problem_log)

        self.presenter.confirm_problem_logged(problem=problem,
                                              problem_log=problem_log)
