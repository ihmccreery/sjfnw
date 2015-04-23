from django.test.utils import override_settings

from sjfnw.grants.tests.base import BaseGrantTestCase
from sjfnw.grants import models

import logging
logger = logging.getLogger('sjfnw')


class GrantReading(BaseGrantTestCase):
  """ Setup: using grant app #1
    Author: testorg@gmail.com (org #2)
    GP: #2, which newacct is a member of, test is not
  """

  fixtures = ['sjfnw/grants/fixtures/test_grants.json',
              'sjfnw/fund/fixtures/test_fund.json']

  def setUp(self):
    pa = models.ProjectApp(application_id=1, giving_project_id=2)
    pa.save()
    award = models.GivingProjectGrant(projectapp_id=pa.pk, amount=8900)
    award.save()
    yer = models.YearEndReport(award=award, total_size=83,
        donations_count_prev=6, donations_count=9,
        other_comments='Critical feedback')
    yer.save()

  def test_author(self):
    self.log_in_test_org()

    response = self.client.get('/grants/view/1', follow=True)

    self.assertTemplateUsed(response, 'grants/reading.html')
    self.assertEqual(3, response.context['perm'])
    self.assertContains(response, 'year end report')

  def test_other_org(self):
    self.log_in_new_org()

    response = self.client.get('/grants/view/1', follow=True)

    self.assertTemplateUsed(response, 'grants/reading.html')
    self.assertEqual(0, response.context['perm'])
    self.assertNotContains(response, 'year end report')

  def test_staff(self):
    self.log_in_admin()

    response = self.client.get('/grants/view/1', follow=True)

    self.assertTemplateUsed(response, 'grants/reading.html')
    self.assertEqual(2, response.context['perm'])
    self.assertContains(response, 'year end report')

  def test_valid_member(self):
    self.log_in_newbie()

    response = self.client.get('/grants/view/1', follow=True)

    self.assertTemplateUsed(response, 'grants/reading.html')
    self.assertEqual(1, response.context['perm'])
    self.assertNotContains(response, 'year end report')

  def test_invalid_member(self):
    self.log_in_testy()

    response = self.client.get('/grants/view/1', follow=True)

    self.assertTemplateUsed(response, 'grants/reading.html')
    self.assertEqual(0, response.context['perm'])
    self.assertNotContains(response, 'year end report')
