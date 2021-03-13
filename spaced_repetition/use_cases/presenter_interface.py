from abc import ABC, abstractmethod

import pandas as pd

from spaced_repetition.domain.problem import Problem
from spaced_repetition.domain.tag import Tag


class PresenterInterface(ABC):
    @staticmethod
    @abstractmethod
    def confirm_problem_created(problem: Problem):
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
    def list_tags(cls, tags: pd.DataFrame) -> None:
        pass
