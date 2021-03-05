from abc import ABC, abstractmethod
from typing import List, Union

from spaced_repetition.domain.problem import Problem
from spaced_repetition.domain.problem_log import ProblemLog


class DBGatewayInterface(ABC):
    @staticmethod
    @abstractmethod
    def create_problem(problem: Problem) -> None:
        pass

    @classmethod
    @abstractmethod
    def get_problems(cls, name: Union[str, None] = None,
                     name_substr: str = None,
                     sorted_by: List[str] = None):
        pass

    @staticmethod
    @abstractmethod
    def create_problem_log(problem_log: ProblemLog) -> None:
        pass
