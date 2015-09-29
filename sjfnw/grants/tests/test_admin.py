from django.core.urlresolvers import reverse

from sjfnw.grants.tests.base import BaseGrantTestCase, LIVE_FIXTURES
from sjfnw.grants import models

import logging
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

class AdminRollover(BaseGrantTestCase):

  url = reverse('sjfnw.grants.views.admin_rollover', kwargs={'app_id': 1})

  def setUp(self):
    super(AdminRollover, self).setUp()
    self.log_in_admin()

  def test_unknown_app(self):
    response = self.client.post(reverse('sjfnw.grants.views.admin_rollover',
                                        kwargs={'app_id': 101}))
    self.assertEqual(response.status_code, 404)

  def test_unknown_cycle(self):
    response = self.client.post(
      reverse('sjfnw.grants.views.admin_rollover', kwargs={'app_id': 1}),
      data={'cycle': u'99'}
    )
    self.assertEqual(response.status_code, 200)
    self.assertIn('Select a valid choice', response.context['form']._errors['cycle'][0])

  def test_app_exists(self):
    self.assertEqual(models.GrantApplication.objects.filter(grant_cycle_id=1).count(), 1)
    response = self.client.post(
      reverse('sjfnw.grants.views.admin_rollover', kwargs={'app_id': 2}),
      data={'cycle': u'1'}
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(models.GrantApplication.objects.filter(grant_cycle_id=1).count(), 1)
    self.assertFalse(response.context['form'].is_valid())

  def test_draft_exists(self):
    self.assertEqual(models.GrantApplication.objects.filter(grant_cycle_id=3).count(), 0)
    self.assertEqual(models.DraftGrantApplication.objects.filter(grant_cycle_id=3).count(), 1)
    response = self.client.post(
      reverse('sjfnw.grants.views.admin_rollover', kwargs={'app_id': 2}),
      data={'cycle': u'3'}
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(models.GrantApplication.objects.filter(grant_cycle_id=3).count(), 0)
    self.assertEqual(models.DraftGrantApplication.objects.filter(grant_cycle_id=3).count(), 1)
    self.assertFalse(response.context['form'].is_valid())

  def test_cycle_closed(self):
    self.assertEqual(models.GrantApplication.objects.filter(grant_cycle_id=4).count(), 0)
    response = self.client.post(
      reverse('sjfnw.grants.views.admin_rollover', kwargs={'app_id': 2}),
      data={'cycle': u'4'}
    )
    self.assertEqual(response.status_code, 302)
    self.assertEqual(models.GrantApplication.objects.filter(grant_cycle_id=4).count(), 1)

  def test_cycle_open(self):
    self.assertEqual(models.GrantApplication.objects.filter(grant_cycle_id=2).count(), 0)
    response = self.client.post(
      reverse('sjfnw.grants.views.admin_rollover', kwargs={'app_id': 2}),
      data={'cycle': u'6'}
    )
    print(response)
    self.assertEqual(response.status_code, 302)
    self.assertRegexpMatches(response.get('Location'), r'/admin/grants/grantapplication/\d/$')
    self.assertEqual(models.GrantApplication.objects.filter(grant_cycle_id=6).count(), 1)
