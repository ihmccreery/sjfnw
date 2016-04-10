from django.core.urlresolvers import reverse

from sjfnw.fund.tests.base import BaseFundTestCase

class GivingProjectPage(BaseFundTestCase):

  url = reverse('sjfnw.fund.views.project_page')

  def setUp(self):
    super(GivingProjectPage, self).setUp()
    self.use_new_acct()

  def test_basic_load(self):

    response = self.client.get(self.url, follow=True)

    self.assertTemplateUsed(response, 'fund/project.html')
