from abc import ABC, abstractmethod
from typing import List

from spaced_repetition.domain.problem import Problem


class PresenterInterface(ABC):
    @staticmethod
    @abstractmethod
    def confirm_problem_created(problem: Problem):
        pass

    @classmethod
    def list_problems(cls, problems: List[Problem]) -> None:
        pass
