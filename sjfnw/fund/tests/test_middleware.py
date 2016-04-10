from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpRequest

from sjfnw import constants as c
from sjfnw.fund import models
from sjfnw.fund.tests.base import BaseFundTestCase
from sjfnw.fund.middleware import MembershipMiddleware

middleware = MembershipMiddleware()

class MockView(object):
  __module__ = 'fund'

class Middleware(BaseFundTestCase):

  def setUp(self):
    super(Middleware, self).setUp()
    self.request = HttpRequest()

  # pylint: disable=no-member
  # for request members added by middleware

  def test_not_authenticated(self):
    self.request.user = AnonymousUser()
    res = middleware.process_view(self.request, MockView(), [], {})
    self.assertEqual(res, None)
    self.assertIsNone(self.request.member)
    self.assertIsNone(self.request.membership)
    self.assertEqual(self.request.membership_status, -1)

  def test_not_member(self):
    self.log_in_admin()
    self.request.user = User.objects.get(email='admin@gmail.com')

    res = middleware.process_view(self.request, MockView(), [], {})
    self.assertEqual(res, None)
    self.assertIsNone(self.request.member)
    self.assertIsNone(self.request.membership)
    self.assertEqual(self.request.membership_status, c.NO_MEMBER)

  def test_no_memberships(self):
    self.log_in_admin()
    self.request.user = User.objects.get(email='admin@gmail.com')
    member = models.Member(email='admin@gmail.com')
    member.save()

    res = middleware.process_view(self.request, MockView(), [], {})
    self.assertEqual(res, None)
    self.assertIsInstance(self.request.member, models.Member)
    self.assertEqual(self.request.member.pk, member.pk)
    self.assertIsNone(self.request.membership)
    self.assertEqual(self.request.membership_status, c.NO_MEMBERSHIP)

  def test_no_approved(self):
    self.log_in_admin()
    self.request.user = User.objects.get(email='admin@gmail.com')
    member = models.Member(email='admin@gmail.com')
    member.save()
    gp = models.GivingProject.objects.get(title='Pre training')
    membership = models.Membership(giving_project=gp, member=member, approved=False)
    membership.save()

    res = middleware.process_view(self.request, MockView(), [], {})
    self.assertEqual(res, None)
    self.assertIsInstance(self.request.member, models.Member)
    self.assertEqual(self.request.member.pk, member.pk)
    self.assertIsInstance(self.request.membership, models.Membership)
    self.assertEqual(self.request.membership.pk, membership.pk)
    self.assertEqual(self.request.membership_status, c.NO_APPROVED)

  def test_approved_not_current(self):
    self.log_in_admin()
    self.request.user = User.objects.get(email='admin@gmail.com')
    member = models.Member(email='admin@gmail.com')
    member.save()
    gp = models.GivingProject.objects.get(title='Pre training')
    membership = models.Membership(giving_project=gp, member=member, approved=True)
    membership.save()

    res = middleware.process_view(self.request, MockView(), [], {})
    self.assertEqual(res, None)
    self.assertIsInstance(self.request.member, models.Member)
    self.assertEqual(self.request.member.pk, member.pk)
    self.assertIsInstance(self.request.membership, models.Membership)
    self.assertEqual(self.request.membership.pk, membership.pk)
    self.assertEqual(self.request.membership_status, c.APPROVED)
