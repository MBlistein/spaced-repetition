from typing import List

from spaced_repetition.domain.problem import ProblemCreator
from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface


class ProblemAdder:
    def __init__(self, db_gateway: DBGatewayInterface):
        self.repo = db_gateway

    def add_problem(self, name: str,
                    difficulty: int,
                    tags: List[str],
                    link: str = None):
        self.repo.create_problem(problem=ProblemCreator().create_problem(
            name=name,
            difficulty=difficulty,
            tags=tags,
            link=link))
