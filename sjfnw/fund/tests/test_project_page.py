from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from sjfnw.fund import models
from sjfnw.fund.tests.base import BaseFundTestCase

import logging, json, unittest
logger = logging.getLogger('sjfnw')


class GivingProjectPage(BaseFundTestCase):

  url = reverse('sjfnw.fund.views.project_page')

  def setUp(self):
    super(GivingProjectPage, self).setUp()
    self.use_new_acct()

  def test_basic_load(self):

    response = self.client.get(self.url, follow=True)

    self.assertTemplateUsed(response, 'fund/project.html')

