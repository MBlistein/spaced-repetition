#!/bin/sh -e

coverage erase
coverage run --parallel-mode --source . -m unittest discover test/unittests -v
coverage run --parallel-mode --source . spaced_repetition/gateways/django_gateway/django_project/manage.py test test/integration_tests -v 2
coverage combine
