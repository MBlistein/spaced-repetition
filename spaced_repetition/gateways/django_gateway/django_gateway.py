from typing import List

from spaced_repetition.domain.problem import Difficulty
from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface

from .django_project.apps.problem.models import Problem


class DjangoGateway(DBGatewayInterface):
    @staticmethod
    def create_problem(difficulty: Difficulty,
                       link: str,
                       name: str,
                       tags: List[str]) -> None:
        Problem.objects.create(
            difficulty=difficulty.value,
            link=link,
            name=name,
            tags=tags)
