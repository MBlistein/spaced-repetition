from typing import List

from spaced_repetition.domain.problem import Difficulty


class DBGatewayInterface:
    @staticmethod
    def create_problem(difficulty: Difficulty,
                       link: str,
                       name: str,
                       tags: List[str]) -> None:
        pass
