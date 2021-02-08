#!/bin/sh -e

coverage erase
coverage run --parallel-mode -m unittest discover test/unittests
coverage run --parallel-mode spaced_repetition/gateways/django_gateway/django_project/manage.py test test/integration_tests
coverage combine
# coverage run -m unittest discover test/unittests
# coverage run spaced_repetition/gateways/django_gateway/django_project/manage.py test test/integration_tests
# python -m unittest discover test/unittests/
# django-admin test test/integration_tests
