import logging

from django.core.urlresolvers import reverse

from sjfnw.fund import models
from sjfnw.fund.tests.base import BaseFundTestCase

logger = logging.getLogger('sjfnw')

class SetCurrent(BaseFundTestCase):

  def setUp(self):
    super(SetCurrent, self).setUp()
    self.use_test_acct()

  def test_not_logged_in(self):
    self.client.logout()

    url = reverse('sjfnw.fund.views.set_current', kwargs={'ship_id': '888'})
    res = self.client.get(url)

    self.assertEqual(res.status_code, 302)
    self.assertEqual(res.url, self.BASE_URL + '/fund/login/?next=' + url)

  def test_unknown_id(self):
    url = reverse('sjfnw.fund.views.set_current', kwargs={'ship_id': '888'})
    res = self.client.get(url)

    self.assertEqual(res.status_code, 302)
    self.assertEqual(res.url, self.BASE_URL + reverse('sjfnw.fund.views.manage_account'))

  def test_valid(self):
    pre_gp = models.GivingProject.objects.get(title='Pre training')
    new_ship = models.Membership(member_id=self.member_id, giving_project=pre_gp, approved=True)
    new_ship.save()

    member = models.Member.objects.get(pk=self.member_id)
    self.assertNotEqual(member.current, new_ship.pk)

    url = reverse('sjfnw.fund.views.set_current', kwargs={'ship_id': new_ship.pk})

    res = self.client.get(url)

    self.assertEqual(res.status_code, 302)
    self.assertEqual(res.url, self.BASE_URL + reverse('sjfnw.fund.views.home'))

    member = models.Member.objects.get(pk=self.member_id)
    self.assertEqual(member.current, new_ship.pk)
