from django.contrib.auth.models import User

from sjfnw.fund import models
from sjfnw.fund.modelutils import create_user, create_membership
from sjfnw.fund.tests.base import BaseFundTestCase, TEST_FIXTURE

import logging, json, unittest
logger = logging.getLogger('sjfnw')

test_email = 'testemail124@gmail.com'

class CreateUser(BaseFundTestCase):

  def setUp(self):
    super(CreateUser, self).setUp()

  def test_member_exists(self):
    existing_member = models.Member(email=test_email, first_name='A', last_name='P')
    existing_member.save()

    error, user, member = create_user(test_email, 'pass', 'anna luisa', 'patino')

    self.assertRegexpMatches(error, 'login')
    self.assertIsNone(user, msg='user should be None')
    self.assertIsNone(member, msg='member should be None')

    user = User.objects.filter(email=test_email)
    self.assertQuerysetEqual(user, [])

  def test_user_exists(self):
    existing_user = User.objects.create_user(test_email, 'pass')

    error, user, member = create_user(test_email, 'pass', 'anna luisa', 'patino')

    self.assertRegexpMatches(error, 'use a different')
    self.assertIsNone(user, msg='user should be None')
    self.assertIsNone(member, msg='member should be None')

    member = models.Member.objects.filter(email=test_email)
    self.assertQuerysetEqual(member, [])

  def test_success(self):
    existing_user = User.objects.filter(email=test_email)
    self.assertQuerysetEqual(existing_user, [])
    existing_member = models.Member.objects.filter(email=test_email)
    self.assertQuerysetEqual(existing_member, [])

    error, user, member = create_user(test_email, 'pass', 'anna luisa', 'patino')

    self.assertIsNone(error)
    self.assertIsInstance(user, User)
    self.assertIsInstance(member, models.Member)

class CreateMembership(BaseFundTestCase):

  def setUp(self):
    super(CreateMembership, self).setUp()

  def test_already_exists(self):
    gp = models.GivingProject.objects.get(title='Pre training')
    member = models.Member(email=test_email, first_name='A', last_name='P')
    member.save()
    existing_ship = models.Membership(member=member, giving_project=gp)
    existing_ship.save()

    error, membership = create_membership(member, gp)

    self.assertRegexpMatches(error, 'already registered')
    self.assertEqual(membership, existing_ship, msg='Returns the pre-existing membership')

  def test_valid(self):
    gp = models.GivingProject.objects.get(title='Pre training')
    member = models.Member(email=test_email, first_name='A', last_name='P')
    member.save()

    error, membership = create_membership(member, gp)

    self.assertIsNone(error)
    self.assertIsInstance(membership, models.Membership)
    self.assertFalse(membership.approved)

  def test_pre_approved(self):
    gp = models.GivingProject.objects.get(title='Pre training')
    gp.pre_approved = test_email
    gp.save()
    member = models.Member(email=test_email, first_name='A', last_name='P')
    member.save()

    error, membership = create_membership(member, gp)

    self.assertIsNone(error)
    self.assertIsInstance(membership, models.Membership)
    self.assertTrue(membership.approved)
