import logging

from django.core import mail
from django.core.urlresolvers import reverse

from sjfnw.fund import models
from sjfnw.fund.tests.base import BaseFundTestCase

logger = logging.getLogger('sjfnw')


class GiftNotifications(BaseFundTestCase):

  url = reverse('sjfnw.fund.views.home')
  cron_url = reverse('sjfnw.fund.views.gift_notify')

  def setUp(self):
    super(GiftNotifications, self).setUp()
    self.use_test_acct()

  def test_no_gift_notification(self):
    response = self.client.get(self.url, follow=True)

    self.assertTemplateUsed(response, 'fund/home.html')
    self.assertNotContains(response, 'gift or pledge received')

  def test_gift_notification(self):
    # enter gift received from donor
    donor = models.Donor.objects.get(pk=self.donor_id)
    donor.received_this = 100
    donor.save()

    # run cron task
    response = self.client.get(self.cron_url, follow=True)
    self.assertEqual(response.status_code, 200)

    # verify notification shows
    response = self.client.get(self.url, follow=True)

    self.assertTemplateUsed(response, 'fund/home.html')
    self.assertContains(response, 'gift or pledge received')

    # verify notification doesn't show on reload
    response = self.client.get(self.url, follow=True)

    self.assertTemplateUsed(response, 'fund/home.html')
    self.assertNotContains(response, 'gift or pledge received')

class PendingApproval(BaseFundTestCase):

  url = reverse('sjfnw.fund.views.new_accounts')

  def setUp(self):
    super(PendingApproval, self).setUp()
    self.use_new_acct()
    pre_ship = models.Membership.objects.get(pk=self.pre_id)
    pre_ship.leader = True
    pre_ship.save()
    post_ship = models.Membership.objects.get(pk=self.post_id)
    post_ship.leader = True
    post_ship.save()

  def test_none(self):
    """ No unapproved memberships -> No email should go out """

    response = self.client.get(self.url, follow=True)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(mail.outbox), 0)

  def test_one(self):

    pre_gp = models.GivingProject.objects.get(title='Pre training')
    member = models.Member(email='abcde@fgh.com', first_name='Ab', last_name='Cd')
    member.save()
    membership = models.Membership(giving_project=pre_gp, member=member)
    membership.save(skip=True)

    response = self.client.get(self.url, follow=True)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(mail.outbox), 1)

  def test_repeat(self):

    pre_gp = models.GivingProject.objects.get(title='Pre training')
    member = models.Member(email='abcde@fgh.com', first_name='Ab', last_name='Cd')
    member.save()
    membership = models.Membership(giving_project=pre_gp, member=member)
    membership.save(skip=True)

    response = self.client.get(self.url, follow=True)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(mail.outbox), 1)

    # will send another email if membership has still not been approved
    response = self.client.get(self.url, follow=True)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(mail.outbox), 2)

    # will not send another after approval
    membership.approved = True
    membership.save()
    self.assertEqual(len(mail.outbox), 3) # approval email

    response = self.client.get(self.url, follow=True)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(mail.outbox), 3) # no additional email to leaders

  def test_multiple(self):
    """ 3 unapproved memberships in 2 GPs -> only 2 emails sent """

    pre_gp = models.GivingProject.objects.get(title='Pre training')
    member = models.Member(email='abcde@fgh.com', first_name='Ab', last_name='Cd')
    member.save()
    membership = models.Membership(giving_project=pre_gp, member=member)
    membership.save(skip=True)

    member = models.Member(email='second@email.com', first_name='Second', last_name='')
    member.save()
    membership = models.Membership(giving_project=pre_gp, member=member)
    membership.save(skip=True)

    post_gp = models.GivingProject.objects.get(title='Post training')
    member = models.Member(email='tres@numero.com', first_name='Three', last_name='Tre')
    member.save()
    membership = models.Membership(giving_project=post_gp, member=member)
    membership.save(skip=True)

    response = self.client.get(self.url, follow=True)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(mail.outbox), 2)

  def test_multiple_leaders(self):
    """ 1 unapproved membership, 3 leaders -> only 1 email """

    pre_gp = models.GivingProject.objects.get(title='Pre training')
    member = models.Member(email='abcde@fgh.com', first_name='Ab', last_name='Cd')
    member.save()
    membership = models.Membership(giving_project=pre_gp, member=member)
    membership.save(skip=True)

    member = models.Member(email='leader@email.com', first_name='Leader', last_name='')
    member.save()
    membership = models.Membership(giving_project=pre_gp, member=member,
        approved=True, leader=True)
    membership.save(skip=True)

    member = models.Member(email='tres@numero.com', first_name='Three', last_name='Tre')
    member.save()
    membership = models.Membership(giving_project=pre_gp, member=member,
        approved=True, leader=True)
    membership.save(skip=True)

    response = self.client.get(self.url, follow=True)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(mail.outbox), 1)

