from django.test.utils import override_settings

from google.appengine.ext import testbed

from sjfnw.grants.tests.base import BaseGrantTestCase
from sjfnw.grants.models import Organization, DraftGrantApplication, GrantApplication

import json, logging
logger = logging.getLogger('sjfnw')


class BaseGrantFilesTestCase(BaseGrantTestCase):
  """ Extension of BaseGrantTestCase that can handle file uploads """

  def setUp(self):
    super(BaseGrantFilesTestCase, self).setUp()
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()

  class Meta:
    abstract = True


def alter_draft_timeline(draft, values):
  """ values: list of timeline widget values (0-14) """
  contents_dict = json.loads(draft.contents)
  for i in range(15):
    contents_dict['timeline_' + str(i)] = values[i]
  draft.contents = json.dumps(contents_dict)
  draft.save()


def alter_draft_files(draft, files_dict):
  """ File list should match this order:
      ['demographics', 'funding_sources', 'budget1', 'budget2',
      'budget3', 'project_budget_file', 'fiscal_letter'] """
  files = dict(zip(DraftGrantApplication.file_fields(), files_dict))
  for key, val in files.iteritems():
    setattr(draft, key, val)
  draft.save()


@override_settings(MEDIA_ROOT='sjfnw/grants/tests/media/',
    DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage',
    FILE_UPLOAD_HANDLERS=('django.core.files.uploadhandler.MemoryFileUploadHandler',))
class ApplySuccessful(BaseGrantFilesTestCase):

  org_id = 2
  cycle_id = 2

  def setUp(self):
    super(ApplySuccessful, self).setUp()
    self.log_in_test_org()

  def test_saved_timeline1(self):
    """ Verify that a timeline with just a complete first row is accepted

    Setup:
      Use same complete draft as test_post_valid_app
      Modify so just first row (first 3 entries of timeline) are filled in.

    Asserts:
      Gets newly created application (throws exception if not created)
      App timeline matches inputted timeline fields
    """

    answers = ['Jan', 'Chillin', 'Not applicable',
               '', '', '', '', '', '', '', '', '', '', '', '']

    draft = DraftGrantApplication.objects.get(organization_id=self.org_id,
                                                     grant_cycle_id=self.cycle_id)
    alter_draft_timeline(draft, answers)

    response = self.client.post('/apply/%d/' % self.cycle_id, follow=True)

    self.assertEqual(response.status_code, 200)
    app = GrantApplication.objects.get(organization_id=self.org_id,
                                              grant_cycle_id=self.cycle_id)
    self.assertEqual(app.timeline, json.dumps(answers))

  def test_saved_timeline5(self):
    """ Verify that a completely filled out timeline is accepted """

    answers = [
      'Jan', 'Chillin', 'Not applicable',
      'Feb', 'Petting dogs', '5 dogs',
      'Mar', 'Planting daffodils', 'Sprouts',
      'July', 'Walking around Greenlake', '9 times',
      'August', 'Reading in the shade', 'No sunburns'
    ]

    draft = DraftGrantApplication.objects.get(organization_id=self.org_id,
                                                     grant_cycle_id=self.cycle_id)
    alter_draft_timeline(draft, answers)

    response = self.client.post('/apply/%d/' % self.cycle_id, follow=True)
    self.assertEqual(response.status_code, 200)
    app = GrantApplication.objects.get(organization_id=self.org_id,
                                              grant_cycle_id=self.cycle_id)
    self.assertEqual(app.timeline, json.dumps(answers))

  def test_mult_budget(self):
    """ scenario: budget1, budget2, budget3

        verify: successful submission & files match  """

    draft = DraftGrantApplication.objects.get(organization_id=self.org_id,
                                              grant_cycle_id=self.cycle_id)
    files = ['funding_sources.docx', 'diversity.doc', 'budget1.docx',
             'budget2.txt', 'budget3.png', '', '']
    alter_draft_files(draft, files)

    response = self.client.post('/apply/%d/' % self.cycle_id, follow=True)

    Organization.objects.get(pk=2)
    self.assertTemplateUsed(response, 'grants/submitted.html')
    app = GrantApplication.objects.get(organization_id=self.org_id, grant_cycle_id=self.cycle_id)
    self.assertEqual(0, DraftGrantApplication.objects
        .filter(organization_id=self.org_id, grant_cycle_id=self.cycle_id)
        .count())
    self.assertEqual(app.budget1, files[2])
    self.assertEqual(app.budget2, files[3])

  def test_profile_updated(self):
    """ Verify that org profile is updated when application is submitted
    Just checks mission field """

    draft = DraftGrantApplication.objects.get(organization_id=self.org_id,
                                              grant_cycle_id=self.cycle_id)
    draft_contents = json.loads(draft.contents)
    org = draft.organization

    self.assertNotEqual(draft_contents['mission'], org.mission)

    response = self.client.post('/apply/%d/' % self.cycle_id, follow=True)

    org = Organization.objects.get(id=self.org_id)
    self.assertTemplateUsed(response, 'grants/submitted.html')
    self.assertEqual(draft_contents['mission'], org.mission)


class ApplyBlocked(BaseGrantTestCase):

  def setUp(self):
    super(ApplyBlocked, self).setUp()
    self.log_in_test_org()

  def test_closed_cycle(self):
    response = self.client.get('/apply/3/')
    self.assertTemplateUsed(response, 'grants/closed.html')

  def test_already_submitted(self):
    self.assertEqual(0,
        DraftGrantApplication.objects.filter(organization_id=2, grant_cycle_id=1).count())

    response = self.client.get('/apply/1/')

    self.assertTemplateUsed(response, 'grants/already_applied.html')
    self.assertEqual(0,
        DraftGrantApplication.objects.filter(organization_id=2, grant_cycle_id=1).count())

  def test_upcoming(self):
    response = self.client.get('/apply/4/')
    self.assertTemplateUsed(response, 'grants/closed.html')

  def test_nonexistent(self):
    response = self.client.get('/apply/79/')
    self.assertEqual(404, response.status_code)


class ApplyValidation(BaseGrantFilesTestCase):
  """TO DO
      fiscal
      collab
      timeline
      files  """

  cycle_id = 2
  org_id = 2

  def setUp(self):
    super(ApplyValidation, self).setUp()
    self.log_in_test_org()

  def test_project_requirements(self):
    """ scenario: support type = project, b1 & b2, no other project info given
        verify: not submitted
                no app created, draft still exists
                form errors - project title, project budget, project budget file """

    draft = DraftGrantApplication.objects.get(pk=2)
    contents_dict = json.loads(draft.contents)
    contents_dict['support_type'] = 'Project support'
    draft.contents = json.dumps(contents_dict)
    draft.save()

    response = self.client.post('/apply/%d/' % self.cycle_id, follow=True)

    self.assertTemplateUsed(response, 'grants/org_app.html')
    self.assertEqual(0, GrantApplication.objects
        .filter(organization_id=self.org_id, grant_cycle_id=self.cycle_id)
        .count())
    self.assertEqual(1, DraftGrantApplication.objects
        .filter(organization_id=self.org_id, grant_cycle_id=self.cycle_id)
        .count())
    self.assertFormError(response, 'form', 'project_title',
        'This field is required when applying for project support.')
    self.assertFormError(response, 'form', 'project_budget',
        'This field is required when applying for project support.')

  def test_timeline_incomplete(self):

    draft = DraftGrantApplication.objects.get(organization_id=self.org_id,
                                              grant_cycle_id=self.cycle_id)
    answers = [
      'Jan', 'Chillin', 'Not applicable',
      'Feb', 'Petting dogs', '5 dogs',
      'Mar', '', 'Sprouts',
      'July', '', '',
      '', 'Reading in the shade', 'No sunburns',]
    alter_draft_timeline(draft, answers)

    response = self.client.post('/apply/%d/' % self.cycle_id, follow=True)
    self.assertFormError(response, 'form', 'timeline',
        '<div class="form_error">All three columns are required for each '
        'quarter that you include in your timeline.</div>')

  def test_timeline_empty(self):

    draft = DraftGrantApplication.objects.get(organization_id=self.org_id,
                                              grant_cycle_id=self.cycle_id)
    answers = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
    alter_draft_timeline(draft, answers)

    response = self.client.post('/apply/%d/' % self.cycle_id, follow=True)
    self.assertFormError(response, 'form', 'timeline',
        '<div class="form_error">This field is required.</div>')


class StartApplication(BaseGrantTestCase):

  def test_load_first_app(self):
    """ Brand new org starting an application
        Page loads
        Form is blank
        Draft is created """

    self.log_in_new_org()
    self.assertEqual(0,
        DraftGrantApplication.objects.filter(organization_id=1, grant_cycle_id=1).count())

    response = self.client.get('/apply/1/')

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'grants/org_app.html')
    self.assertEqual(1,
        DraftGrantApplication.objects.filter(organization_id=1, grant_cycle_id=1).count())

  def test_load_second_app(self):
    """ Org with profile starting an application
        Page loads
        Form has stuff from profile
        Draft is created """

    self.log_in_test_org()
    self.assertEqual(0,
        DraftGrantApplication.objects.filter(organization_id=2, grant_cycle_id=6).count())

    response = self.client.get('/apply/6/')

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'grants/org_app.html')
    org = Organization.objects.get(pk=2)
    self.assertContains(response, org.mission)
    self.assertEqual(1,
        DraftGrantApplication.objects.filter(organization_id=2, grant_cycle_id=6).count())
