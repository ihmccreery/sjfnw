We'll use the example of login form submission and go through how to start writing tests for it. This is for functional/integration tests.

### Brainstorm

It's useful to start by brainstorming the various scenarios you want to test and what you want to verify in each case. Let's say the login form has two fields: email address and password. Here are some possible examples of `POST` requests and what you might expect from each.

- Blank form
    - User is not logged in
    - Response contains login form with 'required' errors on both fields
- Only email is entered
    - User is not logged in
    - Response contains login form with 'required' error on password field
- Only password is entered
    - User is not logged in
    - Response contains login form with 'required' error on email field
- Invalid format for email address
    - User is not logged in
    - Response contains login form with 'invalid' error message on email field
- Email is not registered
    - User is not logged in
    - Response contains login form with 'not registered' error message
- Email is registered, but password is incorrect
    - User is not logged in
    - Response contains login form with 'wrong password' error message
- Email is registered and password is correct (finally!)
    - User is logged in
    - Response redirects to another page

#### Notes on tests

As you can see, a few things are often true:

1. There are a lot of potential tests for just a two-field form
2. There's a lot of repetition in the things we need to verify
3. Some of these seem like they should be a given - if we have a field like `email = forms.EmailField()` that covers the 'email should be required' test (since fields are required by default) and the 'email should be a valid email' test (since `EmailField` comes with validation).

Re: 1 & 2: Tests are very verbose and it's common to spend more time writing tests for a change than you spent on the change itself. Some of the offsetting factors are:
- Having each test cover one small scenario makes it much easier to tell what's broken when tests fail
- It's also very tedious to test something manually unless it's a very tiny change
- You have a record of what is & isn't tested instead of just remembering what you tested manually
- You can reuse these tests after every change, rather than having to re-test things by hand
- The process of writing tests can be helpful in a) clarifying desired behavior and b) catching bugs at the time.

Re: 3: Part of the purpose of tests is to assert what the behavior _should_ be, so that we'll get a warning if it ever changes. The obvious 'email should be required' test will fail if someone adds `required=False` to that field for some reason. So it functions as a sort of confirmation dialog when we change something to go against what we had previously said it should do. We're not really testing whether the `EmailField` validation works, we're saying that this field of the login form should only accept email addresses.

(Also, you'll often be testing more complicated and customized forms than this example)

### Outline tests

You can write down your brainstorming as a list of empty tests.

```python
import unittest

from sjfnw.fund.tests.base import BaseFundTestCase

class LoginForm(BaseFundTestCase):

  @unittest.skip('Incomplete')
  def test_missing_password(self):
    """ Password missing - form error shown, user not logged in """
    pass
```

- `@unittest.skip('Incomplete')` will skip the test, printing out the reason - 'Incomplete', in this case.
- The method name should be somewhat descriptive, to make it easy to identify if the test fails.
- I've recently settled on aiming for a single line docstring that gives an overview of what the test is trying to verify. The details (exact assertions, etc) can be read in the code.
- Note: I recommend snippets for being able to write out a list of test ideas quickly. ([Sublime](http://docs.sublimetext.info/en/latest/extensibility/snippets.html?highlight=snippets))

### Test setup

Often, your tests will share some pre-conditions that you'll want to set up in the class's `setUp` method. For instance, the user may need to be logged in to access the form you want to test, or it may require that certain objects are in the database already. That doesn't apply for this example but see [[Intro to testing|intro-to-testing]] for more info/links.

### Writing a test

A test often has three sections.

1. Verify the starting state
2. Take an action (e.g. send a `POST` request)
3. Verify the response & ending state

Verifying can take different forms, including:  
- Assert something is/isn't in the database  
- Assert the value of a field on a model retrieved from the database  
- Assert various attributes of the response: status code, url, redirects, template used  
- Assert that something is/isn't in the content of the response

An action of POSTing a form can require some preparation to assemble the mocked form data to send.

When you're done outlining and want to start on the tests themselves, you fill them in and then remove the `skip` decorator.

#### Example test

With extra comments to illustrate:

```python
import unittest

from django.contrib.auth.models import User

from sjfnw.fund.tests.base import BaseFundTestCase

class LoginForm(BaseFundTestCase):

  def test_missing_password(self):
    """ Password missing - form error shown, user not logged in """

    # ------ 1. verify starting state ------

    # create User
    User.objects.create_user('abc@gmail.com', 'abc@gmail.com', 'password')

    # ------ 2. take an action - submit form data ------

    # create mock form data
    form_data = {
      'email': 'abc@gmail.com',
      'password': ''
    }

    # make the request
    response = self.client.post('/login', form_data, follow=True)

    # ------ 3. verify response and ending state ------

    self.assertTemplateUsed(response, 'fund/login.html')

    # should be {} if user was not logged in, which evaluates to False
    self.assertFalse(self.client.session)

    # context is the dictionary passed into the render call in the view
    # this assumes the login form was passed in with the key 'form'
    errors = response.context['form'].errors

    self.assertEqual(errors['password'], ['This field is required'])
    self.assertEqual(errors['email'], [])
```

Check the [resources](../resources.md) page for links to more info about testing.
