#!/usr/bin/env bash

# uses coverage package - https://pypi.python.org/pypi/coverage

# run all tests with coverage wrapper
coverage run manage.py test grants fund

# output html results (to dir specified in .coveragerc)
coverage html

echo 'Coverage information collected. See .coverage/index.html'
