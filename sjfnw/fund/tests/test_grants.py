from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from sjfnw.fund import models
from sjfnw.fund.tests.base import BaseFundTestCase, TEST_FIXTURE
from sjfnw.grants.models import ProjectApp

import logging
logger = logging.getLogger('sjfnw')

class Grants(BaseFundTestCase):
  """ Grants listing page """

  fixtures = TEST_FIXTURE + ['sjfnw/fund/fixtures/live_gp_dump.json',
                             'sjfnw/grants/fixtures/orgs.json',
                             'sjfnw/grants/fixtures/grant_cycles.json',
                             'sjfnw/grants/fixtures/apps.json',
                             'sjfnw/grants/fixtures/project_apps.json']
  url = reverse('sjfnw.fund.views.grant_list')

  def setUp(self):
    super(Grants, self).setUp()
    self.use_test_acct()

  def test_grants_display(self):
    """ Verify that assigned grants are shown on grants page

    Setup:
      Use GP 19, create membership for testy

    Asserts:
      Assert that an identifying string for each application appears on page
    """

    member = models.Member.objects.get(email='testacct@gmail.com')
    ship = models.Membership(giving_project_id=19, member=member, approved=True)
    ship.save()
    member.current = ship.pk
    member.save()

    response = self.client.get(self.url)

    papps = ProjectApp.objects.filter(giving_project_id=19).select_related(
        'application', 'application__organization')
    self.assertNotEqual(papps.count(), 0)
    for papp in papps:
      self.assertContains(response, unicode(papp.application.organization))


