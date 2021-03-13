from abc import ABC, abstractmethod
from typing import List, Union

from spaced_repetition.domain.problem import Problem
from spaced_repetition.domain.problem_log import ProblemLog
from spaced_repetition.domain.tag import Tag


class DBGatewayInterface(ABC):
    @staticmethod
    @abstractmethod
    def create_problem(problem: Problem) -> Problem:
        pass

    @classmethod
    @abstractmethod
    def get_problems(cls, name: Union[str, None] = None,
                     name_substr: str = None,
                     sorted_by: List[str] = None,
                     tag_names: List[str] = None) -> List[Problem]:
        pass

    @staticmethod
    @abstractmethod
    def problem_exists(problem_id: int = None, name: str = None) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def create_problem_log(problem_log: ProblemLog) -> None:
        pass

    @classmethod
    @abstractmethod
    def get_problem_logs(cls, problem_ids: List[int] = None) -> List[ProblemLog]:
        pass

    @classmethod
    @abstractmethod
    def create_tag(cls, tag: Tag) -> Tag:
        pass

    @classmethod
    @abstractmethod
    def get_tags(cls, sub_str: str = None):
        pass

    @staticmethod
    def tag_exists(name: str) -> bool:
        pass
