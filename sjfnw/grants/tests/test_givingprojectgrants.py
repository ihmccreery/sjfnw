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
    award = models.GivingProjectGrant(projectapp_id=1, amount=5000,
            first_yer_due=timezone.now().date())
    award.save()

    self.assertEqual(award.total_amount(), award.amount)
    self.assertEqual(award.next_yer_due(), award.first_yer_due)
    self.assertEqual(award.grant_length(), 1)

    self.assertEqual(award.check_number, None)
    self.assertEqual(award.check_mailed, None)

    self.assertEqual(award.second_amount, None)
    self.assertEqual(award.second_check_number, None)
    self.assertEqual(award.second_check_mailed, None)

    self.assertEqual(award.agreement_mailed, None)
    self.assertEqual(award.agreement_returned, None)
    self.assertEqual(award.approved, None)

  def test_two_year_grant(self):
    award = models.GivingProjectGrant(projectapp_id=1, amount=5000,
      second_amount=5000, first_yer_due=timezone.now().date() - timedelta(days=5))
    award.save()

    self.assertEqual(award.total_amount(), award.amount + award.second_amount)
    self.assertEqual(award.grant_length(), 2)

    # still returns first due date even if date has passed
    self.assertEqual(award.next_yer_due(), award.first_yer_due)

    yer = models.YearEndReport(award=award, total_size=10, donations_count=5)
    yer.save()

    # returns second date now that one YER is complete
    second_yer_due = award.first_yer_due.replace(year=award.first_yer_due.year + 1)
    self.assertEqual(award.next_yer_due(), second_yer_due)
