
import sys
from unittest.mock import patch

from django.test import TestCase as DjangoTestCase

from spaced_repetition.controllers.cli_controller import CliController
from spaced_repetition.gateways.django_gateway.django_project.apps.problem.models import (
    Problem as OrmProblem,
    Tag as OrmTag)


class TestCliControllerFullExecution(DjangoTestCase):
    def setUp(self) -> None:
        tag_1 = OrmTag.objects.create(name='tag_1')

        prob_1 = OrmProblem.objects.create(name='prob_1',
                                           difficulty=1)
        prob_1.tags.add(tag_1)

    def test_list_problems(self):
        """ smoke test """
        with patch.object(sys, 'argv', new=['_', 'l']):
            CliController.run()

    def test_add_tag(self):
        with patch.object(sys, 'argv', new=['_', 'add-tag']):
            with patch('builtins.input', return_value='new_tag_name'):
                CliController.run()

                tags = OrmTag.objects.filter(name='new_tag_name')
                self.assertEqual(1, len(tags))
                self.assertEqual('new_tag_name', tags[0].name)
