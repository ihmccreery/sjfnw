#!/usr/bin/env bash

# exit with error code if tests fail
set -e

# run all tests with coverage wrapper
coverage run manage.py test sjfnw

if [ "$1" != "skip-html" ] ; then
  # output html results
  coverage html
  echo 'Coverage information collected. See .coverage-html/index.html'
fi
