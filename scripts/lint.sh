#!/usr/bin/env bash

# run python linter (configured by .pylintrc)
pylint --rcfile=.pylintrc --load-plugins=pylint_django sjfnw

# run javascript linter (configured by .eslintrc)
eslint sjfnw/static/js/*.js
