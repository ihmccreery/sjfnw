from datetime import timedelta
import logging

from django.contrib.auth.models import User
from django.utils import timezone

from sjfnw.fund import models
from sjfnw.tests.base import BaseTestCase

logger = logging.getLogger('sjfnw')


class BaseFundTestCase(BaseTestCase):

  fixtures = ['sjfnw/fund/fixtures/test_fund.json']

  def setUp(self):
    self.create_projects()

  def create_projects(self):
    """ Create pre- and post-training giving projects """
    today = timezone.now()
    gp = models.GivingProject(title="Post training", fund_goal=5000,
        fundraising_training=today - timedelta(days=10),
        fundraising_deadline=today + timedelta(days=80))
    gp.save()
    gp = models.GivingProject(title="Pre training", fund_goal=10000,
        fundraising_training=today + timedelta(days=10),
        fundraising_deadline=today + timedelta(days=30))
    gp.save()

  def login_as_member(self, name):
    """ Expands on method from BaseTestCase, adding additional members """
    error_msg = ''
    try:
      super(BaseFundTestCase, self).login_as_member(name)
      return
    except ValueError, err:
      error_msg = err.message

    if name == "current":
      self.create_test()
      User.objects.create_user('testacct@gmail.com', 'testacct@gmail.com', 'testy')
      self.client.login(username='testacct@gmail.com', password='testy')
    elif name == "new":
      self.create_new()
      User.objects.create_user('newacct@gmail.com', 'newacct@gmail.com', 'noob')
      self.client.login(username='newacct@gmail.com', password='noob')
    else:
      raise ValueError(error_msg + ', "current", "new"')

  def create_test(self):
    """ Sets up "current" membership - in post GP with one donor """

    member = models.Member(email='testacct@gmail.com', first_name='Test',
                           last_name='Member')
    member.save()
    self.member_id = member.pk

    # create membership in post-training gp
    post = models.GivingProject.objects.get(title="Post training")
    ship = models.Membership(giving_project=post, member_id=member.pk, approved=True)
    ship.save()
    self.ship_id = ship.pk
    member.current = ship.pk
    member.save()

    # create donor & step
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
    mem = models.Member(first_name='New', last_name='Member',
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
    self.ship_id = ship.pk
    mem.current = ship.pk
    mem.save()
