import json
import logging

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from google.appengine.ext import testbed
from google.appengine.api import blobstore, datastore

from sjfnw.grants.tests.base import BaseGrantTestCase
from sjfnw.grants.models import (Organization, DraftGrantApplication,
  GrantApplication, GrantCycle)

logger = logging.getLogger('sjfnw')


class BaseGrantFilesTestCase(BaseGrantTestCase):
  """ Subclass of BaseGrantTestCase that can handle file uploads """

  def setUp(self):
    super(BaseGrantFilesTestCase, self).setUp()
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_blobstore_stub()

  def tearDown(self):
    self.testbed.deactivate()

  def create_blob(self, key, **kwargs):
    logger.info(kwargs)
    bs_stub = self.testbed.get_stub('blobstore')
    entity = datastore.Entity(blobstore.BLOB_INFO_KIND, name=key, namespace='')
    entity['size'] = len(kwargs['content'])
    entity['filename'] = kwargs['filename']
    entity['content_type'] = kwargs['content_type']
    datastore.Put(entity)
    bs_stub.storage.CreateBlob('fakeblobkey123', kwargs['content'])

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


class CycleInfo(BaseGrantTestCase):
  url = reverse('sjfnw.grants.views.cycle_info', kwargs={'cycle_id': 1})
  info_url = 'http://www.socialjusticefund.org/grant-app/criminal-justice-grant-cycle-2014'

  def setUp(self):
    super(CycleInfo, self).setUp()

  def test_no_url(self):
    cycle = GrantCycle.objects.get(pk=1)
    self.assertTrue(cycle.is_open())
    self.assertEqual(cycle.info_page, '')

    response = self.client.get(self.url, follow=True)

    self.assertEqual(response.status_code, 404)

  def test_invalid_url(self):
    cycle = GrantCycle.objects.get(pk=1)
    cycle.info_page = 'invalid_url'
    cycle.save()
    self.assertTrue(cycle.is_open())

    response = self.client.get(self.url, follow=True)

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'grants/cycle_info.html')
    self.assertNotContains(response, 'node-grant-portal-info-page')
    self.assertContains(response, 'cycle information page could not be loaded')
    self.assertContains(response, 'a href="invalid_url"')

  def test_valid_url(self):
    cycle = GrantCycle.objects.get(pk=1)
    cycle.info_page = self.info_url
    cycle.save()
    self.assertTrue(cycle.is_open())

    response = self.client.get(self.url, follow=True)

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'grants/cycle_info.html')
    self.assertContains(response, 'node-grant-portal-info-page')
    self.assertNotContains(response, 'cycle information page could not be loaded')


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
    """ Verify that a timeline with just a complete first row is accepted """

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
    self.assertFalse(hasattr(app, 'overflow'))

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

  def test_overflow_created(self):
    """ Verify that GrantApplicationOverflow is created when two_year_question is filled out """

    cycle = GrantCycle.objects.get(pk=self.cycle_id)
    cycle.two_year_grants = True
    cycle.save()

    draft = DraftGrantApplication.objects.get(organization_id=self.org_id,
                                              grant_cycle_id=self.cycle_id)
    draft_contents = json.loads(draft.contents)
    draft_contents['two_year_question'] = 'Year two answer'
    draft.contents = json.dumps(draft_contents)
    draft.save()

    response = self.client.post('/apply/%d/' % self.cycle_id, follow=True)

    self.assertEqual(response.status_code, 200)
    app = GrantApplication.objects.get(organization_id=self.org_id,
                                       grant_cycle_id=self.cycle_id)
    self.assertTrue(hasattr(app, 'overflow'))
    self.assertEqual(app.overflow.two_year_question, u'Year two answer')


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

  ids = {'grant_cycle_id': 2, 'organization_id': 2}

  def setUp(self):
    super(ApplyValidation, self).setUp()
    self.log_in_test_org()

  def test_project_requirements(self):
    draft = DraftGrantApplication.objects.get(pk=2)
    contents_dict = json.loads(draft.contents)
    contents_dict['support_type'] = 'Project support'
    draft.contents = json.dumps(contents_dict)
    draft.save()

    response = self.client.post('/apply/%d/' % self.ids['grant_cycle_id'], follow=True)

    self.assertTemplateUsed(response, 'grants/org_app.html')
    self.assertEqual(0, GrantApplication.objects.filter(**self.ids).count())
    self.assertEqual(1, DraftGrantApplication.objects.filter(**self.ids).count())

    self.assertFormError(response, 'form', 'project_title',
        'This field is required when applying for project support.')
    self.assertFormError(response, 'form', 'project_budget',
        'This field is required when applying for project support.')

  def test_timeline_incomplete(self):
    draft = DraftGrantApplication.objects.get(**self.ids)
    answers = ['Jan', 'Chillin', 'Not applicable',
               'Feb', 'Petting dogs', '5 dogs',
               'Mar', '', 'Sprouts',
               'July', '', '',
               '', 'Reading in the shade', 'No sunburns']
    alter_draft_timeline(draft, answers)

    response = self.client.post('/apply/%d/' % self.ids['grant_cycle_id'], follow=True)
    self.assertFormError(response, 'form', 'timeline',
        '<div class="form_error">All three columns are required for each '
        'quarter that you include in your timeline.</div>')

  def test_timeline_empty(self):
    draft = DraftGrantApplication.objects.get(**self.ids)
    answers = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
    alter_draft_timeline(draft, answers)

    response = self.client.post('/apply/%d/' % self.ids['grant_cycle_id'], follow=True)
    self.assertFormError(response, 'form', 'timeline',
        '<div class="form_error">This field is required.</div>')

  def test_require_two_year(self):
    cycle = GrantCycle.objects.get(pk=self.ids['grant_cycle_id'])
    cycle.two_year_grants = True
    cycle.save()

    response = self.client.post('/apply/%d/' % self.ids['grant_cycle_id'], follow=True)

    self.assertFormError(response, 'form', 'two_year_question', 'This field is required.')


class StartApplication(BaseGrantTestCase):

  def test_load_first_app(self):
    ids = {'organization_id': 1, 'grant_cycle_id': 1}
    self.log_in_new_org()
    self.assertEqual(0, DraftGrantApplication.objects.filter(**ids).count())

    response = self.client.get('/apply/1/')

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'grants/org_app.html')
    self.assertEqual(1, DraftGrantApplication.objects.filter(**ids).count())
    form = response.context['form']
    self.assertFalse(form.fields['two_year_question'].required)

  def test_load_second_app(self):
    ids = {'organization_id': 2, 'grant_cycle_id': 6}
    self.log_in_test_org()
    self.assertEqual(0, DraftGrantApplication.objects.filter(**ids).count())

    response = self.client.get('/apply/6/')

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'grants/org_app.html')
    org = Organization.objects.get(pk=2)
    self.assertEqual(1, DraftGrantApplication.objects.filter(**ids).count())
    # mission should be pre-filled using last application
    self.assertContains(response, org.mission)
    form = response.context['form']
    self.assertFalse(form.fields['two_year_question'].required)

  def test_with_two_year_grant(self):
    ids = {'organization_id': 2, 'grant_cycle_id': 6}
    cycle = GrantCycle.objects.get(pk=ids['grant_cycle_id'])
    cycle.two_year_grants = True
    cycle.save()

    self.log_in_test_org()

    response = self.client.get('/apply/6/')

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'grants/org_app.html')
    self.assertContains(response, cycle.two_year_question)
    form = response.context['form']
    self.assertTrue(form.fields['two_year_question'].required)

class AddFile(BaseGrantFilesTestCase):

  def setUp(self):
    super(AddFile, self).setUp()

  def test_draft_not_found(self):
    url = reverse('sjfnw.grants.views.add_file',
                  kwargs={'draft_type': 'apply', 'draft_id': 0})
    response = self.client.get(url, follow=True)
    self.assertEqual(response.status_code, 404)

  def test_invalid_type(self):
    url = reverse('sjfnw.grants.views.add_file',
                  kwargs={'draft_type': 'what', 'draft_id': 2})
    response = self.client.get(url, follow=True)
    self.assertEqual(response.status_code, 404)

  def test_valid(self):
    draft = DraftGrantApplication.objects.get(pk=2)
    original = draft.budget3

    self.create_blob('fakeblobkey123', filename='file.txt',
                     content_type='text', content='filler')

    url = reverse('sjfnw.grants.views.add_file',
                  kwargs={'draft_type': 'apply', 'draft_id': 2})
    budget = SimpleUploadedFile("file.txt", "blob-key=fakeblobkey123")
    response = self.client.post(url, {'budget3': budget}, follow=True)

    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'file.txt')
    draft = DraftGrantApplication.objects.get(pk=2)
    self.assertEqual(draft.budget3.name, 'fakeblobkey123/file.txt')
    self.assertNotEqual(draft.budget3, original)
