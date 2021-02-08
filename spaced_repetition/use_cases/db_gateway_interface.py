from abc import ABC, abstractmethod

from spaced_repetition.domain.problem import Problem


class DBGatewayInterface(ABC):
    @staticmethod
    @abstractmethod
    def create_problem(problem: Problem) -> None:
        pass
