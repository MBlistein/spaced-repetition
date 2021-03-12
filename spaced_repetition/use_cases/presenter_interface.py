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
    def list_problems(cls, problems: pd.DataFrame) -> None:
        pass

    @classmethod
    def confirm_tag_created(cls, tag: Tag) -> None:
        pass

    @staticmethod
    def _tag_confirmation_txt(tag: Tag) -> str:
        pass
