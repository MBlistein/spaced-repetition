from typing import Union

from django.db.models import QuerySet

import spaced_repetition.domain.problem as domain
from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface

from .django_project.apps.problem.models import Problem


class DjangoGateway(DBGatewayInterface):
    @staticmethod
    def create_problem(problem: domain.Problem) -> None:
        Problem.objects.create(
            difficulty=problem.difficulty.value,
            url=problem.url,
            name=problem.name,
            tags=problem.tags)

    @classmethod
    def get_problems(cls, name: Union[str, None] = None):
        return cls._format_problems(problem_qs=cls._query_problems(name=name))

    @staticmethod
    def _query_problems(name: Union[str, None]):
        qs = Problem.objects.all()
        if name:
            qs = qs.filter(name=name)

        return qs

    @staticmethod
    def _format_problems(problem_qs: QuerySet):
        return [domain.ProblemCreator.create_problem(
            difficulty=p.difficulty,
            name=p.name,
            tags=p.tags,
            url=p.url) for p in problem_qs]
