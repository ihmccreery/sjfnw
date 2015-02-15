from datetime import timedelta
import logging

from django.utils import timezone

from sjfnw.fund import models
from sjfnw.grants.models import ProjectApp
from sjfnw.tests import BaseTestCase

logger = logging.getLogger('sjfnw')


class BaseFundTestCase(BaseTestCase):
  """ Base test case for fundraising tests """

  fixtures = ['sjfnw/fund/fixtures/testy.json']

  def setUp(self):
    self.create_projects()

  def use_test_acct(self):
    self.create_test()
    self.log_in_testy()

  def use_new_acct(self):
    self.create_new()
    self.log_in_newbie()

  def use_admin_acct(self):
    self.log_in_admin()

  def create_projects(self):
    """ Creates pre- and post-training giving projects """
    today = timezone.now()
    gp = models.GivingProject(title="Post training", fund_goal=5000,
        fundraising_training=today-timedelta(days=10),
        fundraising_deadline=today+timedelta(days=80))
    gp.save()
    gp = models.GivingProject(title="Pre training", fund_goal=10000,
        fundraising_training=today+timedelta(days=10),
        fundraising_deadline=today+timedelta(days=30))
    gp.save()

  def create_test(self):
    """ Creates testy membership in Post """
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
    """ Creates newbie member with memberships in pre & post """
    mem = models.Member(first_name='New', last_name='Account',
                        email='newacct@gmail.com')
    mem.save()
    self.member_id = mem.pk
    post = models.GivingProject.objects.get(title="Post training")
    ship = models.Membership(giving_project=post, member=mem, approved=True)
    ship.save()
    self.post_id = ship.pk
    pre = models.GivingProject.objects.get(title='Pre training')
    ship = models.Membership(giving_project=pre, member=mem, approved=True)
    ship.save()
    self.pre_id = ship.pk
    mem.current = ship.pk
    mem.save()
