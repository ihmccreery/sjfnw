#!/usr/bin/env bash

# uses coverage package - https://pypi.python.org/pypi/coverage

# run all tests with coverage wrapper
coverage run --source='sjfnw' --omit='sjfnw/wsgi.py,sjfnw/mail.py,*/tests.py,*__init__.py,*commands/*' manage.py test grants fund

# output html results in /coverage
coverage html -d ~/Projects/coverage
