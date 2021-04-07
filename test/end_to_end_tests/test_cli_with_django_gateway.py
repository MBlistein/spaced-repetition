
import io
import sys
from unittest.mock import patch

from django.test import TestCase as DjangoTestCase

from spaced_repetition.controllers.cli_controller import CliController
from spaced_repetition.domain.problem import Difficulty
from spaced_repetition.gateways.django_gateway.django_project.apps.problem.models import (
    Problem as OrmProblem,
    ProblemLog as OrmProblemLog,
    Tag as OrmTag)


class TestCliControllerFullExecution(DjangoTestCase):
    def setUp(self) -> None:
        tag_1 = OrmTag.objects.create(name='tag_1')

        prob_1 = OrmProblem.objects.create(name='prob_1',
                                           difficulty=1)
        prob_1.tags.add(tag_1)

    def test_list_problems(self):
        with patch.object(sys, 'argv', new=['_', 'l']):
            CliController.run()
