from typing import List, Union

from django.db.models import Count, Q, QuerySet
from django.db.models.functions import Lower

from spaced_repetition.domain.problem import Difficulty, Problem, ProblemCreator
from spaced_repetition.domain.problem_log import ProblemLog
from spaced_repetition.domain.tag import Tag, TagCreator
from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface

from .django_project.apps.problem.models import (Problem as OrmProblem,
                                                 ProblemLog as OrmProblemLog,
                                                 Tag as OrmTag)


class DjangoGateway(DBGatewayInterface):
    @staticmethod
    def create_problem(problem: Problem) -> None:
        existing_tags = OrmTag.objects \
            .filter(name__in=problem.tags)

        if existing_tags.count() < len(problem.tags):
            existing_tags = {e_t.name for e_t in existing_tags}
            non_existing_tags = set(problem.tags).difference(existing_tags)
            raise ValueError("Error, tried to link problem to non-existent "
                             f"tags {non_existing_tags}")

        orm_problem = OrmProblem.objects.create(
            difficulty=problem.difficulty.value,
            url=problem.url,
            name=problem.name)

        orm_problem.tags.set(existing_tags)
        orm_problem.save()

    @classmethod
    def get_problems(cls, name: Union[str, None] = None,
                     name_substr: str = None,
                     sorted_by: List[str] = None,
                     tags: List[str] = None) -> List[Problem]:
        return cls._format_problems(
            problem_qs=cls._query_problems(name=name,
                                           name_substr=name_substr,
                                           sorted_by=sorted_by,
                                           tags=tags))

    @staticmethod
    def _query_problems(name: Union[str, None] = None,
                        name_substr: str = None,
                        sorted_by: List[str] = None,
                        tags: List[str] = None) -> QuerySet:
        qs = OrmProblem.objects.all()
        if name:
            qs = qs.filter(name=name)
        if name_substr:
            qs = qs.filter(name__icontains=name_substr)
        if sorted_by:
            qs = qs.order_by(*sorted_by)
        if tags:
            qs = qs \
                .annotate(num_matches=Count('tags',
                                            filter=Q(tags__name__in=tags))) \
                .filter(num_matches=len(tags))

        return qs

    @staticmethod
    def _format_problems(problem_qs: QuerySet):
        return [ProblemCreator.create_problem(
            difficulty=Difficulty(p.difficulty),
            name=p.name,
            problem_id=p.pk,
            tags=[t.name for t in p.tags.all()],
            url=p.url) for p in problem_qs]

    @staticmethod
    def problem_exists(problem_id: int = None, name: str = None) -> bool:
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
    def _format_problem_logs(problem_log_qs: QuerySet) -> List[ProblemLog]:
        return [ProblemLog(problem_id=pl.problem.pk,
                           action=pl.action,
                           timestamp=pl.timestamp,
                           result=pl.result)
                for pl in problem_log_qs]

    @classmethod
    def create_tag(cls, tag: Tag) -> Tag:
        orm_tag = OrmTag.objects.create(name=tag.name)
        return cls._format_tags(tags=[orm_tag])[0]

    @classmethod
    def get_tags(cls, sort: bool = False, sub_str: str = None):
        return cls._format_tags(tags=cls._query_tags(sort=sort,
                                                     sub_str=sub_str))

    @staticmethod
    def _query_tags(sort: bool = False, sub_str: str = None):
        qs = OrmTag.objects.all()
        if sub_str:
            qs = qs.filter(name__icontains=sub_str)
        if sort:
            qs = qs.order_by(Lower('name'))
        return qs

    @staticmethod
    def _format_tags(tags: Union[List, QuerySet]) -> List[Tag]:
        return [TagCreator.create_tag(name=tag.name, tag_id=tag.pk)
                for tag in tags]

    @staticmethod
    def tag_exists(name: str) -> bool:
        return OrmTag.objects.filter(name=name).exists()
