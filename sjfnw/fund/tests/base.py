from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.utils import timezone

from sjfnw.constants import TEST_MIDDLEWARE
from sjfnw.fund import models, forms
from sjfnw.grants.models import ProjectApp
from sjfnw.tests import BaseTestCase

from datetime import timedelta
import unittest, logging, json
logger = logging.getLogger('sjfnw')


BASE_FIXTURES = ['sjfnw/fund/fixtures/live_gp_dump.json',
                 'sjfnw/fund/fixtures/live_member_dump.json',
                 'sjfnw/fund/fixtures/live_membership_dump.json',
                 'sjfnw/fund/fixtures/live_donor_dump.json']
STEPS_FIXTURE = ['sjfnw/fund/fixtures/live_step_dump.json']
TEST_FIXTURE = ['sjfnw/fund/fixtures/testy.json']


class BaseFundTestCase(BaseTestCase):
  """ Base test case for fundraising tests

  Defines:
    Fixtures (all live dumps)
    setUp
      handles logins based on string passed in
      sets project dates
  """

  def setUp(self, login):
    super(BaseFundTestCase, self).setUp(login)

    self.create_projects()

    if login == 'testy':
      self.create_test()
      self.logInTesty()
    elif login == 'newbie':
      self.create_new()
      self.logInNewbie()
    elif login == 'admin':
      self.logInAdmin()

  def create_projects(self):
    """ Creates pre- and post-training giving projects """
    today = timezone.now()
    gp = models.GivingProject(title="Post training", fund_goal=5000,
        fundraising_training = today - timedelta(days=10),
        fundraising_deadline = today + timedelta(days=80))
    gp.save()
    gp = models.GivingProject(title = "Pre training", fund_goal=10000,
        fundraising_training = today + timedelta(days=10),
        fundraising_deadline = today + timedelta(days=30))
    gp.save()

  def create_test(self):
    """ Creates testy membership in Post. Should be run after loading fixtures """
    post = models.GivingProject.objects.get(title="Post training")
    ship = models.Membership(giving_project=post, member_id=1, approved=True)
    ship.save()
    self.ship_id = ship.pk
    member = models.Member.objects.get(email='testacct@gmail.com')
    member.current = ship.pk
    member.save()
    self.member_id = member.pk
    donor = models.Donor(membership=ship, firstname='Anna', amount=500,
                         talked=True, likelihood=50)
    donor.save()
    self.donor_id = donor.pk
    step = models.Step(donor=donor, description='Talk to about project',
                       created=timezone.now(), date='2013-04-06')
    step.save()
    self.step_id = step.pk

  def create_new(self):
    """ Creates newbie member and associated objs """
    mem = models.Member(first_name='New', last_name='Account',
                        email='newacct@gmail.com')
    mem.save()
    self.member_id = mem.pk
    post = models.GivingProject.objects.get(title="Post training")
    ship = models.Membership(giving_project=post, member = mem, approved=True)
    ship.save()
    self.post_id = ship.pk
    pre = models.GivingProject.objects.get(title='Pre training')
    ship = models.Membership(giving_project=pre, member = mem, approved=True)
    ship.save()
    self.pre_id = ship.pk
    mem.current = ship.pk
    mem.save()
