import logging

from django.core.urlresolvers import reverse

from sjfnw.fund import models
from sjfnw.fund.tests.base import BaseFundTestCase
from sjfnw.grants.models import ProjectApp

logger = logging.getLogger('sjfnw')

class Grants(BaseFundTestCase):
  """ Grants listing page """

  fixtures = ['sjfnw/fund/fixtures/testy.json',
              'sjfnw/fund/fixtures/live_gp_dump.json',
              'sjfnw/grants/fixtures/orgs.json',
              'sjfnw/grants/fixtures/grant_cycles.json',
              'sjfnw/grants/fixtures/apps.json',
              'sjfnw/grants/fixtures/project_apps.json']

  url = reverse('sjfnw.fund.views.grant_list')

  def setUp(self):
    super(Grants, self).setUp()
    self.use_test_acct()

  def test_grants_display(self):
    """ Verify that assigned grants are shown on grants page """

    member = models.Member.objects.get(email='testacct@gmail.com')
    ship = models.Membership(giving_project_id=16, member=member, approved=True)
    ship.save()
    member.current = ship.pk
    member.save()

    response = self.client.get(self.url)

    papps = (ProjectApp.objects.filter(giving_project_id=16)
                               .select_related('application', 'application__organization'))
    self.assertNotEqual(papps.count(), 0)
    for papp in papps:
      if papp.application.pre_screening_status == 45:
        self.assertNotContains(response, unicode(papp.application.organization))
      else:
        self.assertContains(response, unicode(papp.application.organization))
