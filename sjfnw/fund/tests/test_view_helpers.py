import logging

from django.contrib.auth.models import User

from sjfnw.fund import models
from sjfnw.fund.views import _create_user, _create_membership, _compile_membership_progress
from sjfnw.fund.tests.base import BaseFundTestCase

logger = logging.getLogger('sjfnw')
TEST_EMAIL = 'testemail124@gmail.com'

class CreateUser(BaseFundTestCase):

  def setUp(self):
    super(CreateUser, self).setUp()

  def test_member_exists(self):
    existing_member = models.Member(email=TEST_EMAIL, first_name='A', last_name='P')
    existing_member.save()

    error, user, member = _create_user(TEST_EMAIL, 'pass', 'anna luisa', 'patino')

    self.assertRegexpMatches(error, 'login')
    self.assertIsNone(user, msg='user should be None')
    self.assertIsNone(member, msg='member should be None')

    user = User.objects.filter(email=TEST_EMAIL)
    self.assertQuerysetEqual(user, [])

  def test_user_exists(self):
    User.objects.create_user(TEST_EMAIL, 'pass')

    error, user, member = _create_user(TEST_EMAIL, 'pass', 'anna luisa', 'patino')

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

    error, user, member = _create_user(TEST_EMAIL, 'pass', 'anna luisa', 'patino')

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

    error, membership = _create_membership(member, gp)

    self.assertRegexpMatches(error, 'already registered')
    self.assertEqual(membership, existing_ship, msg='Returns the pre-existing membership')

  def test_valid(self):
    gp = models.GivingProject.objects.get(title='Pre training')
    member = models.Member(email=TEST_EMAIL, first_name='A', last_name='P')
    member.save()

    error, membership = _create_membership(member, gp)

    self.assertIsNone(error)
    self.assertIsInstance(membership, models.Membership)
    self.assertFalse(membership.approved)

  def test_pre_approved(self):
    gp = models.GivingProject.objects.get(title='Pre training')
    gp.pre_approved = TEST_EMAIL
    gp.save()
    member = models.Member(email=TEST_EMAIL, first_name='A', last_name='P')
    member.save()

    error, membership = _create_membership(member, gp)

    self.assertIsNone(error)
    self.assertIsInstance(membership, models.Membership)
    self.assertTrue(membership.approved)

class CompileMembershipProgress(BaseFundTestCase):

  def setUp(self):
    super(CompileMembershipProgress, self).setUp()

  def test_empty(self):
    donor_data, progress = _compile_membership_progress([])

    self.assertEqual(donor_data, {})
    for _, value in progress.iteritems():
      self.assertEqual(value, 0)

  def test_single(self):
    # membership with a few donors, some progress
    self.use_test_acct()
    donors = models.Donor.objects.filter(membership_id=self.ship_id)

    donor_data, progress = _compile_membership_progress(donors)

    # TODO detailed assertions
    self.assertIsNotNone(donor_data[self.donor_id])
    self.assertIsNotNone(progress)

  def test_several(self):
    self.use_test_acct()
    membership = models.Membership.objects.get(pk=self.ship_id)
    donors = models.Donor.objects.filter(membership_id=self.ship_id)
    donors = list(donors)
    donor = models.Donor(membership=membership, firstname='Al', lastname='Bautista')
    donor.save()
    donors.append(donor)
    donor = models.Donor(membership=membership, firstname='Alx',
                         lastname='Zereskh', talked=True)
    donor.save()
    donors.append(donor)
    donor = models.Donor(membership=membership, firstname='Irene',
                         lastname='Uadfhaf', talked=True, amount=500, likelihood=40)
    donor.save()
    donors.append(donor)
    donor = models.Donor(membership=membership, firstname='Velcro',
                         lastname='The Cat', talked=True, amount=3,
                         likelihood=1, asked=True)
    donor.save()
    donors.append(donor)

    donor_data, progress = _compile_membership_progress(donors)
    logger.info(donor_data)
    logger.info(progress)
    # TODO finish this test
