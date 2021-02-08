from typing import Union

from django.db.models import QuerySet

from spaced_repetition.domain.problem import Problem, ProblemCreator
from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface

from .django_project.apps.problem import models


class DjangoGateway(DBGatewayInterface):
    @staticmethod
    def create_problem(problem: Problem) -> None:
        models.Problem.objects.create(
            difficulty=problem.difficulty.value,
            url=problem.url,
            name=problem.name,
            tags=problem.tags)

    @classmethod
    def get_problems(cls, name: Union[str, None] = None):
        return cls.format_problems(data=cls.query_problems(name=name))

    @staticmethod
    def query_problems(name: str):
        qs = Problem.objects.all()
        if name:
            qs = qs.filter(name=name)

        return qs

    @staticmethod
    def format_problems(problem_qs: QuerySet):
        return [ProblemCreator.create_problem(
            difficulty=p.difficulty,
            name=p.name,
            tags=p.tags,
            url=p.url) for p in problem_qs]
