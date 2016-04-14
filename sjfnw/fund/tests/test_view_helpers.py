import logging

from django.contrib.auth.models import User

from sjfnw.fund import models
from sjfnw.fund.views import _create_user, _create_membership
from sjfnw.fund.tests.base import BaseFundTestCase

logger = logging.getLogger('sjfnw')
TEST_EMAIL = 'testemail124@gmail.com'

class CreateUser(BaseFundTestCase):

  def setUp(self):
    super(CreateUser, self).setUp()

  def test_member_exists(self):
    existing_member = models.Member(email=TEST_EMAIL, first_name='A', last_name='P')
    existing_member.save()

    user, member, error = _create_user(TEST_EMAIL, 'pass', 'anna luisa', 'patino')

    self.assertRegexpMatches(error, 'login')
    self.assertIsNone(user, msg='user should be None')
    self.assertIsNone(member, msg='member should be None')

    user = User.objects.filter(email=TEST_EMAIL)
    self.assertQuerysetEqual(user, [])

  def test_user_exists(self):
    User.objects.create_user(TEST_EMAIL, 'pass')

    user, member, error = _create_user(TEST_EMAIL, 'pass', 'anna luisa', 'patino')

    self.assertRegexpMatches(error, 'use a different')
    self.assertIsNone(user, msg='user should be None')
    self.assertIsNone(member, msg='member should be None')

    member = models.Member.objects.filter(email=TEST_EMAIL)
    self.assertQuerysetEqual(member, [])

  def test_success(self):
    existing_user = User.objects.filter(email=TEST_EMAIL)
    self.assertQuerysetEqual(existing_user, [])
    existing_member = models.Member.objects.filter(email=TEST_EMAIL)
    self.assertQuerysetEqual(existing_member, [])

    user, member, error = _create_user(TEST_EMAIL, 'pass', 'anna luisa', 'patino')

    self.assertIsNone(error)
    self.assertIsInstance(user, User)
    self.assertIsInstance(member, models.Member)

class CreateMembership(BaseFundTestCase):

  def setUp(self):
    super(CreateMembership, self).setUp()

  def test_already_exists(self):
    gp = models.GivingProject.objects.get(title='Pre training')
    member = models.Member(email=TEST_EMAIL, first_name='A', last_name='P')
    member.save()
    existing_ship = models.Membership(member=member, giving_project=gp)
    existing_ship.save()

    membership, error = _create_membership(member, gp)

    self.assertRegexpMatches(error, 'already registered')
    self.assertEqual(membership, existing_ship, msg='Returns the pre-existing membership')

  def test_valid(self):
    gp = models.GivingProject.objects.get(title='Pre training')
    member = models.Member(email=TEST_EMAIL, first_name='A', last_name='P')
    member.save()

    membership, error = _create_membership(member, gp)

    self.assertIsNone(error)
    self.assertIsInstance(membership, models.Membership)
    self.assertFalse(membership.approved)

  def test_pre_approved(self):
    gp = models.GivingProject.objects.get(title='Pre training')
    gp.pre_approved = TEST_EMAIL
    gp.save()
    member = models.Member(email=TEST_EMAIL, first_name='A', last_name='P')
    member.save()

    membership, error = _create_membership(member, gp)

    self.assertIsNone(error)
    self.assertIsInstance(membership, models.Membership)
    self.assertTrue(membership.approved)
