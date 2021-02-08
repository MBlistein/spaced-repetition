"""Test postgres gateway"""

from django.test import TestCase

import spaced_repetition.domain.problem as domain
from spaced_repetition.gateways.django_gateway.django_gateway import DjangoGateway
from spaced_repetition.gateways.django_gateway.django_project.apps.problem.models import Problem


class TestProblemCreation(TestCase):
    def test_create_problem(self):
        dgw = DjangoGateway()
        prob = domain.Problem(difficulty=domain.Difficulty.EASY,
                              name='testname',
                              url='https://testurl.com',
                              tags=['tag1'])

        dgw.create_problem(problem=prob)

        problems = Problem.objects.all()
        self.assertEqual(problems.count(), 1)

        problem = problems.first()
        self.assertEqual(problem.name, 'testname')
        self.assertEqual(problem.url, 'https://testurl.com')
        self.assertEqual(problem.tags, ['tag1'])


class TestProblemQuerying(TestCase):
    def setUp(self):
        for name in ['name1', 'name2']:
            Problem.objects.create(difficulty=1,
                                   name=name,
                                   tags=['a', 'b'],
                                   url='')

    def test_get_problems(self):
        response = DjangoGateway.get_problems()
        self.assertEqual(2, len(response))
        self.assertIsInstance(response[0], domain.Problem)

    def test_query_all(self):
        self.assertEqual(2, len(DjangoGateway._query_problems(name=None)))

    def test_filter_by_name(self):
        self.assertEqual(1, len(DjangoGateway._query_problems(name='name1')))
