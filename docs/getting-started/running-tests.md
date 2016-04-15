### Run tests

All tests: `./manage.py test sjfnw`

To get more granular, use python `.`-separated paths:

`./manage.py test sjfnw.[module].tests.[test_file].[TestClass].[test_name]`

Examples:

- Only fundraising tests: `./manage.py test sjfnw.fund`  
- Specific test file: `./manage.py test sjfnw.grants.tests.test_admin`  
- Specific test suite: `./manage.py test sjfnw.fund.tests.test_steps.AddStep`  
- Specific test: `./manage.py test sjfnw.fund.tests.test_steps.AddStep.test_valid`

### Test output

Several verbosity levels are available, using `-v`. The default is `1`.

Level | Test display | Logging
:----:|--------------|---------
`0`   | dots         | fatal
`1`   | dots         | error
`2`   | text         | info
`3`   | text         | debug

Dots = single character per test
Text = full line per test

### Coverage

Browse code coverage on [codecov](https://codecov.io/github/aisapatino/sjfnw) (more info: [CI](../workflow/continuous-integration.md)).

To check test coverage locally, install [coverage.py](http://coverage.readthedocs.org/en/latest/) with `pip install coverage`.

Then:

`./scripts/coverage`

Open `./coverage-html/index.html`
