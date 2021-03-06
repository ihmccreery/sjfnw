import logging

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from sjfnw.grants.tests.base import BaseGrantTestCase
from sjfnw.grants import models

logger = logging.getLogger('sjfnw')


class Login(BaseGrantTestCase):

  url = reverse('sjfnw.grants.views.org_login')

  def test_get(self):
    response = self.client.get(self.url, follow=True)
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'grants/org_login_register.html')

  def test_not_registered(self):
    form_data = {
      'email': 'askdhjhakjs@jhasd.com',
      'password': 'apassworD'
    }

    response = self.client.post(self.url, form_data, follow=True)
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'grants/org_login_register.html')
    self.assert_message(response, 'Your password didn\'t match the one on file. Please try again.')

  def test_wrong_pw(self):
    User.objects.create_user('a@b.com', 'a@b.com', 'abc')
    org = models.Organization(email='a@b.com', name='ABC')
    org.save()
    form_data = {
      'email': 'a@b.com',
      'password': 'wrong!'
    }

    response = self.client.post(self.url, form_data, follow=True)
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'grants/org_login_register.html')
    self.assert_message(response, 'Your password didn\'t match the one on file. Please try again.')

  def test_valid(self):
    User.objects.create_user('a@b.com', 'a@b.com', 'abc')
    org = models.Organization(email='a@b.com', name='ABC')
    org.save()
    form_data = {
      'email': 'a@b.com',
      'password': 'abc'
    }

    response = self.client.post(self.url, form_data, follow=True)
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'grants/org_home.html')

class Register(BaseGrantTestCase):

  url = reverse('sjfnw.grants.views.org_register')
  template_success = 'grants/org_home.html'
  template_error = 'grants/org_login_register.html'

  def test_valid_registration(self):
    """ All fields provided, neither email nor name match an org in db """
    registration = {
      'email': 'uniquenewyork@gmail.com',
      'password': 'one',
      'passwordtwo': 'one',
      'organization': 'Unique, New York'
      }

    self.assertEqual(0, models.Organization.objects.filter(name='Unique, New York').count())
    self.assertEqual(0, User.objects.filter(email='uniquenewyork@gmail.com').count())

    response = self.client.post(self.url, registration, follow=True)

    self.assertEqual(1, models.Organization.objects.filter(name='Unique, New York').count())
    self.assertEqual(1, User.objects.filter(email='uniquenewyork@gmail.com').count())
    self.assertTemplateUsed(response, self.template_success)

  def test_repeat_org_name(self):
    """ Verify that registration fails if org with same org name and some email is already in DB.
        Name matches an existing org (email doesn't) """
    registration = {
        'email': 'uniquenewyork@gmail.com',
        'password': 'one',
        'passwordtwo': 'one',
        'organization': 'officemax foundation'
    }

    self.assertEqual(1, models.Organization.objects.filter(name='OfficeMax Foundation').count())
    self.assertEqual(0, User.objects.filter(email='uniquenewyork@gmail.com').count())

    response = self.client.post(self.url, registration, follow=True)

    self.assertEqual(1, models.Organization.objects.filter(name='OfficeMax Foundation').count())
    self.assertEqual(0, User.objects.filter(email='uniquenewyork@gmail.com').count())
    self.assertTemplateUsed(response, self.template_error)
    self.assertFormError(response, 'register', None,
        'That organization is already registered. Log in instead.')

  def test_repeat_org_email(self):
    """ Email matches an existing org (name doesn't) """
    registration = {
        'email': 'neworg@gmail.com',
        'password': 'one',
        'passwordtwo': 'one',
        'organization': 'Brand New'
    }

    self.assertEqual(1, models.Organization.objects.filter(email='neworg@gmail.com').count())
    self.assertEqual(0, models.Organization.objects.filter(name='Brand New').count())

    response = self.client.post(self.url, registration, follow=True)

    self.assertEqual(1, models.Organization.objects.filter(email='neworg@gmail.com').count())
    self.assertEqual(0, models.Organization.objects.filter(name='Brand New').count())
    self.assertTemplateUsed(response, self.template_error)
    self.assertFormError(response, 'register', None,
        'That email is already registered. Log in instead.')

  def test_repeat_user_email(self):
    """ Email matches a user, but email/name don't match an org """
    User.objects.create_user('bababa@gmail.com', 'neworg@gmail.com', 'noob')

    registration = {
        'email': 'bababa@gmail.com',
        'password': 'one',
        'passwordtwo': 'one',
        'organization': 'Brand New'
    }

    self.assertEqual(1, User.objects.filter(email='neworg@gmail.com').count())
    self.assertEqual(0, models.Organization.objects.filter(name='Brand New').count())

    response = self.client.post(self.url, registration, follow=True)

    self.assertEqual(1, User.objects.filter(email='neworg@gmail.com').count())
    self.assertEqual(0, models.Organization.objects.filter(name='Brand New').count())
    self.assertTemplateUsed(response, self.template_error)
    self.assertFormError(response, 'register', None,
        'That email is registered with Project Central. Please register using a different email.')

  def test_admin_entered_match(self):
    """ Org name matches an org that was entered by staff (no login email) """

    org = models.Organization(name='Ye olde Orge')
    org.save()

    registration = {
      'email': 'bababa@gmail.com',
      'password': 'one',
      'passwordtwo': 'one',
      'organization': 'Ye olde Orge'
    }

    response = self.client.post(self.url, registration, follow=True)

    org = models.Organization.objects.get(name='Ye olde Orge')
    # org email was updated
    self.assertEqual(org.email, registration['email'])
    # user was created, is_active = False
    self.assertEqual(1, User.objects.filter(email='bababa@gmail.com', is_active=False).count())
    # stayed on login page
    self.assertTemplateUsed(response, self.template_error)
    # message telling them to contact admin
    self.assert_message(response, ('You have registered successfully but your '
        'account needs administrator approval. Please contact '
        '<a href="mailto:info@socialjusticefund.org">info@socialjusticefund.org</a>'))
