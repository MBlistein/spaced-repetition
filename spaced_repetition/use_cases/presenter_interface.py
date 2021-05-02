from abc import ABC, abstractmethod

import pandas as pd

from spaced_repetition.domain.problem import Problem
from spaced_repetition.domain.problem_log import ProblemLog
from spaced_repetition.domain.tag import Tag


class PresenterInterface(ABC):
    @classmethod
    @abstractmethod
    def confirm_problem_created(cls, problem: Problem):
        pass

    @staticmethod
    @abstractmethod
    def confirm_problem_logged(problem: Problem, problem_log: ProblemLog):
        pass

    @classmethod
    @abstractmethod
    def confirm_tag_created(cls, tag: Tag) -> None:
        pass

    @classmethod
    @abstractmethod
    def list_problems(cls, problems: pd.DataFrame) -> None:
        pass

    @classmethod
    @abstractmethod
    def list_problem_tag_combos(cls, problem_tag_combos: pd.DataFrame) -> None:
        pass

    @classmethod
    @abstractmethod
    def show_problem_history(cls, problem: Problem,
                             problem_log_info: pd.DataFrame) -> None:
        pass

    @classmethod
    @abstractmethod
    def list_tags(cls, tags: pd.DataFrame) -> None:
        pass
