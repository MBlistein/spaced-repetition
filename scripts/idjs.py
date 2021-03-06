"""Ipython shell with pre-configured Django and all models loaded
Allows to manually inspect and modify the database."""

import django
import logging
import os
import sys

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'spaced_repetition.gateways.django_gateway.django_project.django_project.settings')
django.setup()

from spaced_repetition.domain.problem import Difficulty
from spaced_repetition.domain.problem_log import Action, Result
from spaced_repetition.gateways.django_gateway.django_project.apps.problem.models import *


LOGGER = logging.getLogger('django.db.backends')


def main():
    # set logger to debugging from command line
    args = sys.argv[1:]
    if args:
        if args[0] == 'debug':
            LOGGER.setLevel(logging.DEBUG)
            LOGGER.addHandler(logging.StreamHandler())

    print("\n----------- spaced-repetiion idb ------------")
    print(f"Django is set up for {os.environ['DJANGO_SETTINGS_MODULE']}")


if __name__ == "__main__":
    main()

