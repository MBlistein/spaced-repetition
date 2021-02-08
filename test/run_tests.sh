#!/bin/sh -e

python -m unittest discover test/unittests/
django-admin test test/integration_tests
