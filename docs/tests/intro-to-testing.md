### Current state of tests in sjfnw

Most of the existing tests check the response returned by a view, and often also use queries to verify that expected objects were created/updated/deleted.. As we refactor some views into smaller pieces, we can write more unit tests.

One major issue with existing tests is that we don't have any way to test the actual in-browser behavior, including javascript functionality like loading and submitting forms or autosaving the grant application. There's an issue filed [here](https://github.com/aisapatino/sjfnw/issues/172).

At this point, the primary goal is to add [test coverage](../workflow/continuous-integration.md) in whatever ways seem best. In particular, we should **avoid adding any new functionality without accompanying tests**.

### Django and Python testing

Django and Python provide a lot of tools/infrastructure for testing. To start:

- Tests use a sqlite3 database, which is in-memory and much faster than using mysql. (configured in [`settings.py`](https://github.com/aisapatino/sjfnw/blob/master/sjfnw/settings.py#L33))
- A test database is created at the start and destroyed after all tests have run. Between tests, the database is restored to its prior state, so one test's changes in the db should not affect another test.
- If fixtures are specified, they will be loaded into the db before each test.

All of our test classes inherit from [`django.test.TestCase`](https://docs.djangoproject.com/en/1.8/topics/testing/overview/#testcase), which inherits from Python's [`unittest.TestCase`](https://docs.python.org/2/library/unittest.html#unittest.TestCase). This provides all our test classes with

- Optional `setUp` and `tearDown` methods, which, if specified, will run before & after each individual test. `setUp` is often useful, for example for logging the user in before each test.
- Assertions are provided as methods on the test class. Python provides some [basic ones](https://docs.python.org/2/library/unittest.html#assert-methods) and Django adds [additional ones](https://docs.djangoproject.com/en/1.8/topics/testing/overview/#assertions)
- Django provides a [test client](https://docs.djangoproject.com/en/1.8/topics/testing/overview/#module-django.test.client) that can make requests

Note: We have sub-classed Django's `TestCase` as `BaseTestCase`, which is further specialized as `BaseFundTestCase` and `BaseGrantTestCase`. They provide a few convenient shortcuts for common tasks like creating a User and logging them in. See [docs for test classes](test-classes.md)

### Test files

Tests are located in `sjfnw/fund/tests/` and `sjfnw/grants/tests/`

- Split tests into separate files by subject/view
- Files all start with `test_` (to be found by the test runner)

`sjfnw/tests.py` houses test-related classes and methods that are useful across both modules. For instance: custom test runner, base test classes, custom assertion methods, etc.
