from typing import List, Union

from django.db.models import QuerySet

from spaced_repetition.domain.problem import Difficulty, Problem, ProblemCreator
from spaced_repetition.domain.problem_log import ProblemLog
from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface

from .django_project.apps.problem.models import Problem as OrmProblem
from .django_project.apps.problem.models import ProblemLog as OrmProblemLog


class DjangoGateway(DBGatewayInterface):
    @staticmethod
    def create_problem(problem: Problem) -> None:
        OrmProblem.objects.create(
            difficulty=problem.difficulty.value,
            url=problem.url,
            name=problem.name,
            tags=problem.tags)

    @classmethod
    def get_problems(cls, name: Union[str, None] = None,
                     name_substr: str = None,
                     sorted_by: List[str] = None):
        return cls._format_problems(
            problem_qs=cls._query_problems(name=name,
                                           name_substr=name_substr,
                                           sorted_by=sorted_by))

    @staticmethod
    def _query_problems(name: Union[str, None],
                        name_substr: str = None,
                        sorted_by: List[str] = None):
        qs = OrmProblem.objects.all()
        if name:
            qs = qs.filter(name=name)
        if name_substr:
            qs = qs.filter(name__icontains=name_substr)
        if sorted_by:
            qs = qs.order_by(*sorted_by)

        return qs

    @staticmethod
    def _format_problems(problem_qs: QuerySet):
        return [ProblemCreator.create_problem(
            difficulty=Difficulty(p.difficulty),
            name=p.name,
            problem_id=p.pk,
            tags=p.tags,
            url=p.url) for p in problem_qs]

    @staticmethod
    def problem_exists(problem_id: int = None, name: str = None):
        if bool(problem_id) == bool(name):
            raise ValueError("Supply exactly one of 'problem_id' or 'name'!")
        if problem_id:
            return OrmProblem.objects.filter(pk=problem_id).exists()
        return OrmProblem.objects.filter(name=name).exists()

    @staticmethod
    def create_problem_log(problem_log: ProblemLog) -> None:
        orm_problem_log = OrmProblemLog(
            problem=OrmProblem.objects.get(pk=problem_log.problem_id),
            action=problem_log.action,
            result=problem_log.result)

        if problem_log.timestamp:
            orm_problem_log.timestamp = problem_log.timestamp

        orm_problem_log.save()

    @classmethod
    def get_problem_logs(cls):
        return cls._format_problem_logs(
            problem_qs=cls._query_problem_logs())

    @staticmethod
    def _query_problem_logs():
        qs = OrmProblemLog.objects.all()
        return qs

    @staticmethod
    def _format_problem_logs(problem_log_qs: QuerySet):
        return [ProblemLog(problem_id=pl.problem.pk,
                           action=pl.action,
                           timestamp=pl.timestamp,
                           result=pl.result)
                for pl in problem_log_qs]
