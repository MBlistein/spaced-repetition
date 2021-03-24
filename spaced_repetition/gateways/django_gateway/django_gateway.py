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

        return cls._format_problems(problems=[orm_problem])[0]

    @classmethod
    def get_problems(cls, name: Union[str, None] = None,
                     name_substr: str = None,
                     sorted_by: List[str] = None,
                     tag_names: List[str] = None) -> List[Problem]:
        return cls._format_problems(
            problems=cls._query_problems(name=name,
                                         name_substr=name_substr,
                                         sorted_by=sorted_by,
                                         tag_names=tag_names))

    @staticmethod
    def _query_problems(name: Union[str, None] = None,
                        name_substr: str = None,
                        sorted_by: List[str] = None,
                        tag_names: List[str] = None) -> QuerySet:
        qs = OrmProblem.objects.all()
        if name:
            qs = qs.filter(name=name)
        if name_substr:
            qs = qs.filter(name__icontains=name_substr)
        if sorted_by:
            qs = qs.order_by(*sorted_by)
        if tag_names:
            qs = qs \
                .annotate(num_matches=Count('tags',
                                            filter=Q(tags__name__in=tag_names))) \
                .filter(num_matches=len(tag_names))

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

    @staticmethod
    def create_problem_log(problem_log: ProblemLog) -> None:
        OrmProblemLog.objects.create(
            ease=problem_log.ease,
            interval=problem_log.interval,
            problem=OrmProblem.objects.get(pk=problem_log.problem_id),
            result=problem_log.result.value,
            timestamp=problem_log.timestamp)

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
        for idx, p_l in enumerate(problem_log_qs):
            res.append(ProblemLogCreator.create(
                ease=p_l.ease,
                interval=p_l.interval,
                problem_id=p_l.problem.pk,
                timestamp=p_l.timestamp,
                result=Result(p_l.result)))

        return res

    @classmethod
    def create_tag(cls, tag: Tag) -> Tag:
        orm_tag = OrmTag.objects.create(name=tag.name)
        return cls._format_tags(tags=[orm_tag])[0]

    @classmethod
    def get_tags(cls, sub_str: str = None):
        return cls._format_tags(tags=cls._query_tags(sub_str=sub_str))

    @staticmethod
    def _query_tags(sub_str: str = None):
        qs = OrmTag.objects.all()
        if sub_str:
            qs = qs.filter(name__icontains=sub_str)
        return qs

    @staticmethod
    def _format_tags(tags: Union[List, QuerySet]) -> List[Tag]:
        return [TagCreator.create_tag(name=tag.name, tag_id=tag.pk)
                for tag in tags]

    @staticmethod
    def tag_exists(name: str) -> bool:
        return OrmTag.objects.filter(name=name).exists()
