"""Test postgres gateway"""

from django.test import TestCase

from spaced_repetition.domain.problem import Difficulty
from spaced_repetition.gateways.django_gateway.django_gateway import DjangoGateway
from spaced_repetition.gateways.django_gateway.django_project.apps.problem.models import Problem


class TestProblemCreation(TestCase):
    def test_create_problem(self):
        dgw = DjangoGateway()
        dgw.create_problem(difficulty=Difficulty.EASY,
                           name='testname',
                           link='https://testlink.com',
                           tags=['tag1'])

        problems = Problem.objects.all()
        self.assertEqual(problems.count(), 1)

        problem = problems.first()
        self.assertEqual(problem.name, 'testname')
        self.assertEqual(problem.link, 'https://testlink.com')
        self.assertEqual(problem.tags, ['tag1'])
