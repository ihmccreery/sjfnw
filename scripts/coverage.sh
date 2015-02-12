#!/usr/bin/env bash

# run all tests with coverage wrapper
coverage run manage.py test fund grants

if [ "$1" != "skip-html" ] ; then
  # output html results
  coverage html
  echo 'Coverage information collected. See .coverage-html/index.html'
fi
