"""Test postgres gateway"""

from django.test import TestCase

from spaced_repetition.domain.problem import Difficulty, Problem
from spaced_repetition.gateways.django_gateway.django_gateway import DjangoGateway
from spaced_repetition.gateways.django_gateway.django_project.apps.problem import models


class TestProblemCreation(TestCase):
    def test_create_problem(self):
        dgw = DjangoGateway()
        prob = Problem(difficulty=Difficulty.EASY,
                       name='testname',
                       url='https://testurl.com',
                       tags=['tag1'])

        dgw.create_problem(problem=prob)

        problems = models.Problem.objects.all()
        self.assertEqual(problems.count(), 1)

        problem = problems.first()
        self.assertEqual(problem.name, 'testname')
        self.assertEqual(problem.url, 'https://testurl.com')
        self.assertEqual(problem.tags, ['tag1'])
