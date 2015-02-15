import logging
import unittest

from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from sjfnw.fund import models
from sjfnw.fund.tests.base import BaseFundTestCase

logger = logging.getLogger('sjfnw')

class Home(BaseFundTestCase):

  url = reverse('sjfnw.fund.views.home')

  def setUp(self):
    super(Home, self).setUp()
    self.use_new_acct()

  def test_new(self):
    """ Verify that add mult form is shown to new memberships """

    # using pre-training membership

    membership = models.Membership.objects.get(pk=self.pre_id)

    response = self.client.get(self.url, follow=True)

    self.assertTemplateUsed(response, 'fund/add_mult_flex.html')
    self.assertEqual(response.context['request'].membership, membership)
    self.assertNotContains(response, 'likelihood')

    # using post-training membership

    member = models.Member.objects.get(pk=self.member_id)
    member.current = self.post_id
    member.save()
    membership = models.Membership.objects.get(pk=self.post_id)

    response = self.client.get(self.url, follow=True)

    self.assertTemplateUsed(response, 'fund/add_mult_flex.html')
    self.assertEqual(response.context['request'].membership, membership)
    self.assertContains(response, 'likelihood')

  def test_contacts_without_est(self):
    """ Going to home page with contacts that do not have estimates """

    # using pre-training membership
    membership = models.Membership.objects.get(pk=self.pre_id)

    # create contacts without amount or likelihood
    contact1 = models.Donor(firstname='Anna', membership=membership)
    contact1.save()
    contact2 = models.Donor(firstname='Banana', membership=membership)
    contact2.save()

    response = self.client.get(self.url)

    # verify estimates form is not shown
    self.assertEqual(response.context['request'].membership, membership)
    self.assertTemplateNotUsed('fund/add_estimates.html')

    # using post-training membership
    member = membership.member
    member.current = self.post_id
    member.save()

    membership = models.Membership.objects.get(pk=self.post_id)

    # move created contacts to current membership
    contact1.membership = membership
    contact1.save()
    contact2.membership = membership
    contact2.save()

    response = self.client.get(self.url, follow=True)

    # verify estimates form is shown
    self.assertTemplateUsed('fund/add_estimates.html')
    self.assertEqual(response.context['request'].membership, membership)

  def test_estimates_done(self):
    """ Verify add estimates form is not shown if contacts have estimates """

    # use post-training membership
    membership = models.Membership.objects.get(pk=self.post_id)
    member = membership.member
    member.current = self.post_id
    member.save()

    # create contacts with amount & likelihood
    contact = models.Donor(firstname='Anna', membership=membership, amount=0, likelihood=0)
    contact.save()
    contact = models.Donor(firstname='Banana', membership=membership, amount=567, likelihood=34)
    contact.save()

    response = self.client.get(self.url)

    # verify estimates form is not shown
    self.assertTemplateNotUsed('fund/add_estimates.html')
    self.assertEqual(response.context['request'].membership, membership)

  @unittest.skip('Incomplete')
  def test_contacts_list(self):
    """ Verify correct display of a long contact list with steps, history

    Setup:
      Use membership 96 (test & gp 10) which has 29 contacts

    Asserts:
      ASSERTIONS
    """

    self.log_in_testy()
    member = models.Member.objects.get(pk=1)
    member.current = 96
    member.save()

    response = self.client.get(self.url)

  @unittest.skip('Incomplete')
  def test_gift_notification(self):
    pass

    """ add a gift to donor
        test that notif shows up on next load
        test that notif is gone on next load """


class HomeSurveys(BaseFundTestCase):

  url = reverse('sjfnw.fund.views.home')

  def setUp(self):
    super(HomeSurveys, self).setUp()
    self.use_test_acct()

  @unittest.skip('Incomplete')
  def test_survey_shown(self):
    pass

  @unittest.skip('Incomplete')
  def test_surveys_complete(self):
    pass
