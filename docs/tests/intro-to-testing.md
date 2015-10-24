### Basics

Tests generally consist of a combination of actions and assertions. Assertions are used to describe the outcome you expect. If an assertion fails, it will raise an exception, and that test will stop running and be considered 'failed'.

[Django testing overview](https://docs.djangoproject.com/en/1.8/topics/testing/overview/) has a lot of good information.

### Types of tests

There are many terms for types of tests, and they're often used differently by different people. For our purposes, we'll go with some basic definitions:

**Unit tests** test a single small piece of your code - for instance, a single method. They shouldn't require dependencies or complex setup - they test a section of code in isolation, essentially. They don't use the test client.

**Functional/integration tests**
Functional tests are often defined as verifying a certain function from the user's perspective - e.g. 'When I load this url, I expect to see these things on the page'.  Integration tests are focused on testing that multiple parts of the app work together. For instance, 'If I submit this form, I expect that a new Donor model will be created with these properties.' We tend to go for a combo approach where we test what is in the response as well as what effects that has on the database. These tests take more setup, often use fixtures and usually revolve around http requests though the test client.

### Current state of tests in sjfnw

Most of our tests are functional/integrational, focusing on a specific view, often involving at least one form and model. They are the easiest type to write given the way our code is set up and they test a lot of parts of the app. As we refactor some code into smaller pieces, we can write more unit tests, like these ones for [`_compile_membership_progress`](https://github.com/aisapatino/sjfnw/blob/master/sjfnw/fund/tests/test_home.py#L139).

One major issue with our tests is that we don't have any way to test our front-end javascript. There is some key functionality there - things like loading and submitting forms, autosaving the grant application. There's an issue filed [here](https://github.com/aisapatino/sjfnw/issues/172).

At this point, the primary goal is to add [test coverage](../workflow/continuous-integration.md) in whatever ways seem best. In particular, we should **avoid adding any new functionality without accompanying tests**.

### Django and Python testing

Django and Python provide a lot of tools/infrastructure for testing. To start:

- Due to our [database settings](https://github.com/aisapatino/sjfnw/blob/master/sjfnw/settings.py#L33), the tests will use a sqlite3 database (in-memory and much faster than using a local mysql).
- A test databases is created at the start and destroyed after all tests have run. Between tests, the database is restored to its prior state, so one test's changes in the db should not affect another test.
- If fixtures are specified, they will be loaded into the db before each test.

All of our test classes inherit from [`django.test.TestCase`](https://docs.djangoproject.com/en/1.8/topics/testing/overview/#testcase), which inherits from Python's [`unittest.TestCase`](https://docs.python.org/2/library/unittest.html#unittest.TestCase). This provides all our test classes with

- Optional `setUp` and `tearDown` methods, which, if specified, will run before & after each individual test. `setUp` is often useful, for example for logging the user in before each test.
- Assertions are provided as methods on the test class. Python provides some [basic ones](https://docs.python.org/2/library/unittest.html#assert-methods) and Django adds [additional ones](https://docs.djangoproject.com/en/1.8/topics/testing/overview/#assertions)
- Django provides a [test client](https://docs.djangoproject.com/en/1.8/topics/testing/overview/#module-django.test.client) that can make requests

Note: We have sub-classed Django's `TestCase` as `BaseTestCase`, which is further specialized as `BaseFundTestCase` and `BaseGrantTestCase`. They just provide a few convenient shortcuts for common tasks like creating a User and logging them in.

### Test files

Tests are located in `sjfnw/fund/tests/` and `sjfnw/grants/tests/`
- Split tests into separate files by subject
- Files all start with `test_` (to be found by the test runner)

`sjfnw/tests.py` houses test-related classes and methods that are useful across both modules. For instance: custom test runner, base test classes, custom assertion methods, etc.

### Organizing tests

In Django, test classes represent test suites - bundles of tests that share a `setUp` method, fixtures, etc.

```python
from sjfnw.fund.tests.base import BaseFundTestCase

class LoginForm(BaseFundTestCase):
```

A basic test class can inherit from `django.test.TestCase`, but more frequently you'll be using the fundraising base test case above, or the one in grants.

Test methods have to start with `test_`. Meaning you can include helper methods (not tests themselves, but used by tests) as long as they don't use that prefix.

I usually structure it like this:

- A file has tests relating to a theme (`test_steps.py`, `test_home.py`, etc).
- Inside the file, there's a class for each smaller breakdown of the theme, e.g. `AddStep`, `CompleteStep`, `EditStep`
- If the file gets too long, you can split it into pieces. One class per file or multiple classes per file are ok.
- Each class can have a `setUp` method that runs before *each* individual test method.
- Individual test methods test different scenarios related to the same form, model, etc.

See [writing tests](writing-tests) for an in-depth example.
