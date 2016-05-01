from django.core.urlresolvers import reverse

from sjfnw.fund.models import Member
from sjfnw.fund.tests.base import BaseFundTestCase

class Support(BaseFundTestCase):

  url = reverse('sjfnw.fund.views.support')

  def setUp(self):
    super(Support, self).setUp()

  def test_logged_out(self):
    res = self.client.get(self.url)

    self.assertEqual(res.status_code, 200)
    self.assertTemplateUsed(res, 'fund/support.html')
    self.assertFalse(res.context['member'])

  def test_logged_in(self):
    self.login_as_member('current')

    res = self.client.get(self.url)

    self.assertEqual(res.status_code, 200)
    self.assertTemplateUsed(res, 'fund/support.html')
    self.assertIsInstance(res.context['member'], Member)

  def test_logged_in_no_ship(self):
    self.login_as_admin()
    member = Member(email='admin@gmail.com')
    member.save()

    res = self.client.get(self.url)

    self.assertEqual(res.status_code, 200)
    self.assertTemplateUsed(res, 'fund/support.html')
    self.assertIsInstance(res.context['member'], Member)
