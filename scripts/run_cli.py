"""Script to start command line interface"""

# pylint: disable=E402

import django
import os
os.environ['DJANGO_SETTINGS_MODULE'] = \
    'spaced_repetition.gateways.django_gateway.django_project.django_project.settings'
django.setup()

from spaced_repetition.controllers.cli_controller import main


if __name__ == "__main__":
    main()
