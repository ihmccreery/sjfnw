from datetime import timedelta
import logging

from django.core import mail
from django.core.urlresolvers import reverse
from django.utils import timezone

from sjfnw.fund import models
from sjfnw.fund.tests.base import BaseFundTestCase

logger = logging.getLogger('sjfnw')


class GiftNotifications(BaseFundTestCase):

  url = reverse('sjfnw.fund.views.home')
  cron_url = reverse('sjfnw.fund.cron.gift_notify')

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

  def test_gift_notification_next(self):
    # enter gift received from donor for next year
    donor = models.Donor.objects.get(pk=self.donor_id)
    donor.received_next = 100
    donor.save()

    # run cron task
    response = self.client.get(self.cron_url, follow=True)
    self.assertEqual(response.status_code, 200)

    # verify notification shows
    response = self.client.get(self.url, follow=True)

    self.assertTemplateUsed(response, 'fund/home.html')
    self.assertContains(response, 'gift or pledge received')


class PendingApproval(BaseFundTestCase):

  url = reverse('sjfnw.fund.cron.new_accounts')

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


class OverdueEmails(BaseFundTestCase):

  url = reverse('sjfnw.fund.cron.email_overdue')

  def setUp(self):
    super(OverdueEmails, self).setUp()
    self.use_new_acct()

    # create 2 donors on new member's pre membership
    donor = models.Donor(firstname='En', membership_id=self.pre_id)
    donor.save()
    self.donor1 = donor.pk
    donor = models.Donor(firstname='Tva', membership_id=self.pre_id)
    donor.save()
    self.donor2 = donor.pk

    # create another member, membership, donor
    member = models.Member(email='two@gmail.com', first_name='Two')
    member.save()
    gp = models.GivingProject.objects.get(title='Post training')
    membership = models.Membership(giving_project=gp, member=member, approved=True)
    membership.save()
    donor = models.Donor(firstname='Tre', membership=membership)
    donor.save()
    self.donor3 = donor.pk

  def test_none(self):
    self.assertEqual(len(mail.outbox), 0)
    response = self.client.get(self.url, follow=True)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(mail.outbox), 0)

  def test_several(self):
    """ overdue step in two memberships (different members) """
    step = models.Step(donor_id=self.donor1, date=timezone.now()-timedelta(days=3))
    step.save()
    step = models.Step(donor_id=self.donor3, date=timezone.now()-timedelta(days=9))
    step.save()

    self.assertEqual(len(mail.outbox), 0)
    response = self.client.get(self.url, follow=True)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(mail.outbox), 2)

    # doesn't send emails again
    response = self.client.get(self.url, follow=True)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(mail.outbox), 2)

  def test_several_per_donor(self):
    """ Two overdue steps for one membership; expect only one email """

    step = models.Step(donor_id=self.donor1, date=timezone.now()-timedelta(days=3))
    step.save()
    step = models.Step(donor_id=self.donor2, date=timezone.now()-timedelta(days=9))
    step.save()

    self.assertEqual(len(mail.outbox), 0)
    response = self.client.get(self.url, follow=True)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(mail.outbox), 1)

    membership = models.Membership.objects.get(pk=self.pre_id)
    assertEqual(membership.emailed.day, timezone().now().date().day)

  def test_same_member(self):
    """ overdue step in two memberships for same member """
    donor = models.Donor(membership_id=self.post_id, firstname='Other')
    donor.save()

    step = models.Step(donor_id=self.donor1, date=timezone.now()-timedelta(days=3))
    step.save()
    step = models.Step(donor=donor, date=timezone.now()-timedelta(days=9))
    step.save()

    self.assertEqual(len(mail.outbox), 0)
    response = self.client.get(self.url, follow=True)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(mail.outbox), 2)

  def test_completed(self):
    """ overdue step in two memberships (different members) """
    now = timezone.now()
    step = models.Step(donor_id=self.donor1, date=now-timedelta(days=3), completed=now)
    step.save()
    step = models.Step(donor_id=self.donor3, date=ow-timedelta(days=9), completed=now)
    step.save()

    self.assertEqual(len(mail.outbox), 0)
    response = self.client.get(self.url, follow=True)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(mail.outbox), 0)
