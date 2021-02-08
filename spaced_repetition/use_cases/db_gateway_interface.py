from abc import ABC, abstractmethod
from typing import Union

from spaced_repetition.domain.problem import Problem


class DBGatewayInterface(ABC):
    @staticmethod
    @abstractmethod
    def create_problem(problem: Problem) -> None:
        pass

    @classmethod
    @abstractmethod
    def get_problems(cls, name: Union[str, None] = None):
        pass
