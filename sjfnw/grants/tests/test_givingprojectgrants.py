from datetime import timedelta
import logging

from django.utils import timezone

from sjfnw.grants import models
from sjfnw.grants.tests.base import BaseGrantTestCase

logger = logging.getLogger('sjfnw')

class NewGivingProjectGrant(BaseGrantTestCase):
  """ Test GivingProjectGrant model methods """

  def setUp(self):
    super(NewGivingProjectGrant, self).setUp()

  def test_minimum_grant_information(self):
    award = models.GivingProjectGrant(projectapp_id=1, amount=5000)
    award.save()

    self.assertEqual(award.yearend_due(), None)
    self.assertEqual(award.check_number, None)
    self.assertEqual(award.check_mailed, None)

    self.assertEqual(award.second_amount, None)
    self.assertEqual(award.second_check_number, None)
    self.assertEqual(award.second_check_mailed, None)

    self.assertEqual(award.agreement_mailed, None)
    self.assertEqual(award.agreement_returned, None)
    self.assertEqual(award.approved, None)

  def test_single_year_grant(self):
    award = models.GivingProjectGrant(projectapp_id=1, amount=5000,
                                      agreement_mailed=timezone.now().date())
    award.save()

    self.assertEqual(award.total_amount(), award.amount)
    self.assertEqual(award.yearend_due(), award.agreement_mailed.replace(
                       year=award.agreement_mailed.year + 1))
    self.assertEqual(award.grant_length(), 1)
    self.assertEqual(award.second_check_mailed, None)

  def test_two_year_grant(self):
    today = timezone.now().date()
    award = models.GivingProjectGrant(projectapp_id=1, amount=5000,
      second_amount=5000, agreement_mailed=today - timedelta(days=366))
    award.save()

    self.assertEqual(award.total_amount(), award.amount + award.second_amount)
    self.assertEqual(award.grant_length(), 2)

    first_yer_due = award.agreement_mailed.replace(year=award.agreement_mailed.year + 1)
    self.assertEqual(award.yearend_due(), first_yer_due)

    award.second_check_mailed = today
    award.save()
    second_yer_due = award.agreement_mailed.replace(year=award.agreement_mailed.year + 2)
    self.assertEqual(award.yearend_due(), second_yer_due)
