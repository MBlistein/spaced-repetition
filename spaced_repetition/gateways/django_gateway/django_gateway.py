from typing import List, Union

from django.db.models import Count, Q, QuerySet

from spaced_repetition.domain.problem import Difficulty, Problem, ProblemCreator
from spaced_repetition.domain.problem_log import (ProblemLog, ProblemLogCreator,
                                                  Result)
from spaced_repetition.domain.tag import Tag, TagCreator
from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface

from .django_project.apps.problem.models import (Problem as OrmProblem,
                                                 ProblemLog as OrmProblemLog,
                                                 Tag as OrmTag)


class DjangoGateway(DBGatewayInterface):
    @classmethod
    def create_problem(cls, problem: Problem) -> Problem:
        orm_problem = OrmProblem.objects.create(
            difficulty=problem.difficulty.value,
            url=problem.url,
            name=problem.name)

        orm_problem.tags.set(OrmTag.objects.filter(name__in=problem.tags))
        orm_problem.save()

        return cls._format_problems(problems=[orm_problem])[0]

    @classmethod
    def get_problems(cls, name: Union[str, None] = None,
                     name_substr: str = None,
                     tags_any: List[str] = None,
                     tags_all: List[str] = None) -> List[Problem]:
        return cls._format_problems(
            problems=cls._query_problems(name=name,
                                         name_substr=name_substr,
                                         tags_any=tags_any,
                                         tags_all=tags_all))

    @staticmethod
    def _query_problems(name: str = None,
                        name_substr: str = None,
                        tags_any: List[str] = None,
                        tags_all: List[str] = None) -> QuerySet:
        qs = OrmProblem.objects.all()
        if name is not None:
            qs = qs.filter(name=name)
        if name_substr:
            qs = qs.filter(name__icontains=name_substr)
        if tags_any is not None:
            qs = qs \
                .filter(tags__name__in=tags_any) \
                .distinct()
        if tags_all:
            qs = qs \
                .annotate(num_matches=Count(
                    'tags',
                    filter=Q(tags__name__in=tags_all))) \
                .filter(num_matches=len(tags_all))

        return qs

    @staticmethod
    def _format_problems(problems: Union[List, QuerySet]) -> List[Problem]:
        return [ProblemCreator.create(
            difficulty=Difficulty(p.difficulty),
            name=p.name,
            problem_id=p.pk,
            tags=[t.name for t in p.tags.all()],
            url=p.url) for p in problems]

    @staticmethod
    def problem_exists(problem_id: int = None, name: str = None) -> bool:
        if bool(problem_id) == bool(name):
            raise ValueError("Supply exactly one of 'problem_id' or 'name'!")
        if problem_id:
            return OrmProblem.objects.filter(pk=problem_id).exists()
        return OrmProblem.objects.filter(name=name).exists()

    @classmethod
    def create_problem_log(cls, problem_log: ProblemLog) -> None:
        log = OrmProblemLog.objects.create(
            comment=problem_log.comment,
            problem=OrmProblem.objects.get(pk=problem_log.problem_id),
            result=problem_log.result.value,
            timestamp=problem_log.timestamp)

        log.tags.set(cls._query_tags(
            names=[tag.name for tag in problem_log.tags], sub_str=None))

    @classmethod
    def get_problem_logs(cls, problem_ids: List[int] = None) -> List[ProblemLog]:
        return cls._format_problem_logs(
            problem_log_qs=cls._query_problem_logs(problem_ids=problem_ids))

    @staticmethod
    def _query_problem_logs(problem_ids: List[int] = None):
        qs = OrmProblemLog.objects.all()

        if problem_ids:
            qs = qs.filter(problem__pk__in=problem_ids)

        return qs

    @staticmethod
    def _format_problem_logs(problem_log_qs: QuerySet) -> List[ProblemLog]:
        res = []
        for p_l in problem_log_qs:
            res.append(ProblemLogCreator.create(
                comment=p_l.comment,
                problem_id=p_l.problem.pk,
                result=Result(p_l.result),
                tags=[TagCreator.create(name=tag.name, tag_id=tag.pk)
                      for tag in p_l.tags.all()],
                timestamp=p_l.timestamp))

        return res

    @classmethod
    def create_tag(cls, tag: Tag) -> Tag:
        orm_tag = OrmTag.objects.create(name=tag.name)
        return cls._format_tags(tags=[orm_tag])[0]

    @classmethod
    def get_tags(cls, names: List[str] = None, sub_str: str = None):
        return cls._format_tags(tags=cls._query_tags(names=names,
                                                     sub_str=sub_str))

    @staticmethod
    def _query_tags(names: Union[List[str], None], sub_str: Union[str, None]):
        qs = OrmTag.objects.all()
        if names is not None:
            qs = qs.filter(name__in=names)
        if sub_str:
            qs = qs.filter(name__icontains=sub_str)
        return qs

    @staticmethod
    def _format_tags(tags: Union[List, QuerySet]) -> List[Tag]:
        return [TagCreator.create(name=tag.name, tag_id=tag.pk)
                for tag in tags]

    @staticmethod
    def tag_exists(name: str) -> bool:
        return OrmTag.objects.filter(name=name).exists()
