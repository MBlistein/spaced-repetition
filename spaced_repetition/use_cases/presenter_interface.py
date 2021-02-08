from abc import ABC, abstractmethod

from spaced_repetition.domain.problem import Problem


class PresenterInterface(ABC):
    @staticmethod
    @abstractmethod
    def confirm_problem_created(problem: Problem):
        pass
