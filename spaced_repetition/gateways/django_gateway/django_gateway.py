from spaced_repetition.domain.problem import Problem
from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface

from .django_project.apps.problem import models


class DjangoGateway(DBGatewayInterface):
    @staticmethod
    def create_problem(problem: Problem) -> None:
        models.Problem.objects.create(
            difficulty=problem.difficulty.value,
            link=problem.link,
            name=problem.name,
            tags=problem.tags)
