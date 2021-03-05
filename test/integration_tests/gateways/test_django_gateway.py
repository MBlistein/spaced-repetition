"""Test postgres gateway"""

import datetime as dt

from dateutil.tz import tzlocal
from django.test import TestCase

from spaced_repetition.domain.problem import Difficulty, Problem
from spaced_repetition.domain.problem_log import Action, ProblemLog, Result
from spaced_repetition.gateways.django_gateway.django_gateway import DjangoGateway
from spaced_repetition.gateways.django_gateway.django_project.apps.problem.models import (
    Problem as OrmProblem,
    ProblemLog as OrmProblemLog)


class TestProblemCreation(TestCase):
    def test_create_problem(self):
        dgw = DjangoGateway()
        prob = Problem(difficulty=Difficulty.EASY,
                       name='testname',
                       problem_id=99,
                       tags=['tag1'],
                       url='https://testurl.com')

        dgw.create_problem(problem=prob)

        problems = OrmProblem.objects.all()
        self.assertEqual(problems.count(), 1)

        problem = problems.first()
        self.assertEqual(problem.name, 'testname')
        self.assertNotEqual(problem.pk, 99)  # pk is independent of problem_id
        self.assertEqual(problem.url, 'https://testurl.com')
        self.assertEqual(problem.tags, ['tag1'])


class TestProblemQuerying(TestCase):
    def setUp(self):
        for name in ['name1', 'name2']:
            OrmProblem.objects.create(difficulty=1,
                                      name=name,
                                      tags=['a', 'b'],
                                      url='')

    def test_get_problems(self):
        response = DjangoGateway.get_problems()
        self.assertEqual(2, len(response))
        self.assertIsInstance(response[0], Problem)

    def test_query_all(self):
        self.assertEqual(2, len(DjangoGateway._query_problems(name=None)))

    def test_filter_by_name(self):
        self.assertEqual(1, len(DjangoGateway._query_problems(name='name1')))

    def test_problem_exists_via_name(self):
        self.assertTrue(DjangoGateway.problem_exists(name='name1'))

    def test_problem_does_not_exist_via_name(self):
        self.assertFalse(DjangoGateway.problem_exists(name='not there'))

    def test_problem_exists_via_problem_id(self):
        problem_id = OrmProblem.objects.last().pk

        self.assertTrue(DjangoGateway.problem_exists(problem_id=problem_id))

    def test_problem_does_not_exist_problem_id(self):
        self.assertFalse(DjangoGateway.problem_exists(problem_id=99999999))

    def test_problem_exists_raises_when_no_input(self):
        with self.assertRaises(ValueError) as context:
            DjangoGateway.problem_exists()

        self.assertEqual(str(context.exception),
                         "Supply exactly one of 'problem_id' or 'name'!")

    def test_problem_exists_raises_when_all_inputs(self):
        with self.assertRaises(ValueError) as context:
            DjangoGateway.problem_exists(name='test', problem_id=1)

        self.assertEqual(str(context.exception),
                         "Supply exactly one of 'problem_id' or 'name'!")


class TestProblemLog(TestCase):
    def setUp(self):
        OrmProblem.objects.create(difficulty=Difficulty.EASY.value,
                                  name='testname',
                                  tags=['tag1'],
                                  url='https://testurl.com')

    def test_create_problem_log_no_timestamp(self):
        dgw = DjangoGateway()
        log = ProblemLog(
            action=Action.CREATE.value,
            problem_id=1,
            result=Result.SOLVED_OPTIMALLY_SLOWER.value)

        ts_before = dt.datetime.now(tz=tzlocal())
        dgw.create_problem_log(problem_log=log)
        ts_after = dt.datetime.now(tz=tzlocal())

        self.assertEqual(OrmProblemLog.objects.count(), 1)

        orm_log = OrmProblemLog.objects.first()
        self.assertEqual(orm_log.action, Action.CREATE.value)
        self.assertEqual(orm_log.problem.name, 'testname')
        self.assertEqual(orm_log.result, Result.SOLVED_OPTIMALLY_SLOWER.value)
        self.assertGreater(orm_log.timestamp, ts_before)
        self.assertLess(orm_log.timestamp, ts_after)

    def test_create_problem_log_with_timestamp(self):
        dgw = DjangoGateway()
        ts = dt.datetime(2021, 3, 6, 10, 0, tzinfo=tzlocal())
        log = ProblemLog(
            action=Action.CREATE.value,
            problem_id=1,
            result=Result.SOLVED_OPTIMALLY_SLOWER.value,
            timestamp=ts)

        dgw.create_problem_log(problem_log=log)

        self.assertEqual(OrmProblemLog.objects.count(), 1)

        orm_log = OrmProblemLog.objects.first()
        self.assertEqual(orm_log.action, Action.CREATE.value)
        self.assertEqual(orm_log.problem.name, 'testname')
        self.assertEqual(orm_log.result, Result.SOLVED_OPTIMALLY_SLOWER.value)
        self.assertEqual(orm_log.timestamp, ts)
