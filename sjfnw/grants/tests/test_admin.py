from sjfnw.grants.tests.base import BaseGrantTestCase, LIVE_FIXTURES
from sjfnw.grants import models

import logging, unittest
logger = logging.getLogger('sjfnw')


class AdminInlines(BaseGrantTestCase):
  """ Verify basic display of related inlines for grants objects in admin """

  fixtures = LIVE_FIXTURES

  def setUp(self): #don't super, can't set cycle dates with this fixture
    self.log_in_admin()

  def test_organization(self):
    """ Verify that related inlines show existing objs

    Setup:
      Log in as admin, go to org #
      Orgs 41, 154, 156 have application, draft, gp grant

    Asserts:
      Application inline
    """

    organization = models.Organization.objects.get(pk=41)

    app = organization.grantapplication_set.all()[0]

    response = self.client.get('/admin/grants/organization/41/')

    self.assertContains(response, app.grant_cycle.title)
    self.assertContains(response, app.pre_screening_status)

  def test_givingproject(self):
    """ Verify that assigned grant applications (projectapps) are shown as inlines

    Setup:
      Find a GP that has projectapps

    Asserts:
      Displays one of the assigned apps
    """

    apps = models.ProjectApp.objects.filter(giving_project_id=19)

    response = self.client.get('/admin/fund/givingproject/19/')

    self.assertContains(response, 'selected="selected">' + str(apps[0].application))

  def test_application(self):
    """ Verify that gp assignment and awards are shown on application page

    Setup:
      Use application with GP assignment. App 274, Papp 3
    """

    papp = models.ProjectApp.objects.get(pk=3)

    response = self.client.get('/admin/grants/grantapplication/274/')

    self.assertContains(response, papp.giving_project.title)
    self.assertContains(response, papp.screening_status)


class AdminRevert(BaseGrantTestCase):

  def setUp(self):
    super(AdminRevert, self).setUp()
    self.log_in_admin()

  def test_load_revert(self):

    response = self.client.get('/admin/grants/grantapplication/1/revert')

    self.assertEqual(200, response.status_code)
    self.assertContains(response, 'Are you sure you want to revert this application into a draft?')

  def test_revert_app(self):
    """ scenario: revert submitted app pk1
        verify:
          draft created
          app gone
          draft fields match app (incl cycle, timeline) """

    self.assertEqual(0,
        models.DraftGrantApplication.objects.filter(organization_id=2, grant_cycle_id=1).count())
    app = models.GrantApplication.objects.get(organization_id=2, grant_cycle_id=1)

    self.client.post('/admin/grants/grantapplication/1/revert')

    self.assertEqual(1,
      models.DraftGrantApplication.objects.filter(organization_id=2, grant_cycle_id=1).count())
    draft = models.DraftGrantApplication.objects.get(organization_id=2, grant_cycle_id=1)
    self.assert_draft_matches_app(draft, app)

@unittest.skip('Incomplete')
class AdminRollover(BaseGrantTestCase):

  def setUp(self):
    super(AdminRollover, self).setUp()
    self.log_in_admin()
