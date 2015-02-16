import logging
import unittest

from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from sjfnw.fund import models
from sjfnw.fund.tests.base import BaseFundTestCase

logger = logging.getLogger('sjfnw')


class HomeNotifications(BaseFundTestCase):

  url = reverse('sjfnw.fund.views.home')
  cron_url = reverse('sjfnw.fund.views.gift_notify')

  def setUp(self):
    super(HomeNotifications, self).setUp()
    self.use_test_acct()

  def test_no_gift_notification(self):

    response = self.client.get(self.url, follow=True)

    self.assertTemplateUsed(response, 'fund/home.html')
    self.assertNotContains(response, 'gift or pledge received')

  def test_gift_notification(self):
    donor = models.Donor.objects.get(pk=self.donor_id)
    donor.received_this = 100
    donor.save()

    response = self.client.get(self.cron_url, follow=True)

    self.assertEqual(response.status_code, 200)

    response = self.client.get(self.url, follow=True)

    self.assertTemplateUsed(response, 'fund/home.html')
    self.assertContains(response, 'gift or pledge received')

    response = self.client.get(self.url, follow=True)

    self.assertTemplateUsed(response, 'fund/home.html')
    self.assertNotContains(response, 'gift or pledge received')

