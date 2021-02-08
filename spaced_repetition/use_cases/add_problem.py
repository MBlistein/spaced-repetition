from typing import List

from spaced_repetition.domain.problem import Difficulty, ProblemCreator
from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface
from spaced_repetition.use_cases.presenter_interface import PresenterInterface


class ProblemAdder:
    def __init__(self, db_gateway: DBGatewayInterface,
                 presenter: PresenterInterface):
        self.repo = db_gateway
        self.present = presenter

    def add_problem(self, name: str,
                    difficulty: Difficulty,
                    tags: List[str],
                    link: str = None):
        problem = ProblemCreator.create_problem(
            name=name,
            difficulty=difficulty,
            tags=tags,
            link=link)
        self.repo.create_problem(problem=problem)
        self.present.confirm_problem_created(problem=problem)
