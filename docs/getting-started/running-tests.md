#### Running tests

Run all tests:

`./manage.py test sjfnw`

To get more granular, use python `.`-separated paths:

`./manage.py test sjfnw.[module].tests.[test_file].[TestClass].[test_name]`

Examples:

Only fundraising tests: `./manage.py test sjfnw.fund`  
Specific test file: `./manage.py test sjfnw.grants.tests.test_admin`  
Specific test suite: `./manage.py test sjfnw.fund.tests.test_steps.AddStep`  
Specific test: `./manage.py test sjfnw.fund.tests.test_steps.AddStep.test_valid`

#### Coverage

Browse code coverage on [codecov](https://codecov.io/github/aisapatino/sjfnw) (more info: [CI](../workflow/continuous-integration.md)).

To check test coverage locally, install [coverage.py](http://nedbatchelder.com/code/coverage/), then do

`./scripts/coverage`

then open `./coverage-html/index.html`
