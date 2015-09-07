from sjfnw.fund.models import Donor
from sjfnw.fund.tests.base import BaseFundTestCase

class TotalPromised(BaseFundTestCase):

  def setUp(self):
    super(TotalPromised, self).setUp()
    self.use_new_acct()

  def test_no_promise(self):
    donor = Donor(membership_id=self.pre_id, firstname='Hello', amount=20, likelihood=75)
    donor.save()
    self.assertEqual(donor.total_promised(), 0)
