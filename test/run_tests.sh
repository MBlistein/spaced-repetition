#!/bin/bash

coverage erase
coverage run --parallel-mode --source spaced_repetition -m unittest discover test/unittests -v
coverage run --parallel-mode --source spaced_repetition spaced_repetition/gateways/django_gateway/django_project/manage.py test test/integration_tests -v 2

if [[ -n "$1" ]] && [[ "$1" == "full" ]]; then
    echo 'Run end-to-end tests:';
    coverage run --parallel-mode --source spaced_repetition spaced_repetition/gateways/django_gateway/django_project/manage.py test test/end_to_end_tests -v 2
fi

coverage combine
coverage html
