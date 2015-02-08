from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from sjfnw.constants import TEST_MIDDLEWARE
from sjfnw.fund import models
from sjfnw.fund.tests.base import BaseFundTestCase, TEST_FIXTURE

import logging, json, unittest
logger = logging.getLogger('sjfnw')

@override_settings(MIDDLEWARE_CLASSES = TEST_MIDDLEWARE,
    PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',))
class GivingProjectPage(BaseFundTestCase):

  url = reverse('sjfnw.fund.views.project_page')

  fixtures = TEST_FIXTURE

  def setUp(self):
    super(GivingProjectPage, self).setUp()
    self.use_new_acct()

  def test_basic_load(self):

    response = self.client.get(self.url, follow=True)

    self.assertTemplateUsed(response, 'fund/page_project.html')

