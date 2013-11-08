from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.utils import timezone

from google.appengine.ext import testbed

from sjfnw.constants import TEST_MIDDLEWARE
from sjfnw.tests import BaseTestCase
from sjfnw.fund.models import GivingProject
from sjfnw.grants.models import GrantApplication, DraftGrantApplication, Organization, GrantCycle, GrantAward

import sys, datetime, json, unittest
import logging
logger = logging.getLogger('sjfnw')


""" NOTE: some tests depend on having these files in sjfnw/media
  budget.docx      diversity.doc      funding_sources.docx
  budget1.docx     budget2.txt         budget3.png  """

def setCycleDates():
  """ Updates grant cycle dates to make sure they have the expected statuses:
      open, open, closed, upcoming, open """

  now = timezone.now()
  ten_days = datetime.timedelta(days=10)

  cycle = GrantCycle.objects.get(pk=1)
  cycle.open = now - ten_days
  cycle.close = now + ten_days
  cycle.save()
  twenty_days = datetime.timedelta(days=20)
  cycle = GrantCycle.objects.get(pk=2)
  cycle.open = now - ten_days
  cycle.close = now + ten_days
  cycle.save()
  cycle = GrantCycle.objects.get(pk=3)
  cycle.open = now - twenty_days
  cycle.close = now - ten_days
  cycle.save()
  cycle = GrantCycle.objects.get(pk=4)
  cycle.open = now + ten_days
  cycle.close = now + twenty_days
  cycle.save()
  cycle = GrantCycle.objects.get(pk=5)
  cycle.open = now - twenty_days
  cycle.close = now + ten_days
  cycle.save()

class BaseGrantTestCase(BaseTestCase):
  """ Base for grants tests. Provides fixture and basic setUp
      as well as several helper functions """

  fixtures = ['sjfnw/grants/fixtures/test_grants.json']

  def setUp(self, login):
    super(BaseGrantTestCase, self).setUp(login)
    if login == 'testy':
      self.logInTestorg()
    elif login == 'newbie':
      self.logInNeworg()
    elif login == 'admin':
      self.logInAdmin()
    setCycleDates()

  class Meta:
    abstract = True

def alterDraftTimeline(draft, values):
  """ values: list of timeline widget values (0-14) """
  contents_dict = json.loads(draft.contents)
  for i in range(15):
    contents_dict['timeline_' + str(i)] = values[i]
  draft.contents = json.dumps(contents_dict)
  draft.save()

def alterDraftFiles(draft, files_dict):
  """ File list should match this order:
      ['budget', 'demographics', 'funding_sources', 'budget1', 'budget2',
      'budget3', 'project_budget_file', 'fiscal_letter'] """
  files = dict(zip(DraftGrantApplication.file_fields(), files_dict))
  for key, val in files.iteritems():
    setattr(draft, key, val)
  draft.save()

def assertDraftAppMatch(self, draft, app, exclude_cycle): #only checks fields in draft
  """ Timeline formats:
        submitted: json'd list, in order, no file names
        draft: mixed in with other contents by widget name: timeline_0 - timeline_14 """
  draft_contents = json.loads(draft.contents)
  app_timeline = json.loads(app.timeline)
  for field, value in draft_contents.iteritems():
    if 'timeline' in field:
      i = int(field.split('_')[-1])
      self.assertEqual(value, app_timeline[i])
    else:
      self.assertEqual(value, getattr(app, field))
  for field in GrantApplication.file_fields():
    self.assertEqual(getattr(draft, field), getattr(app, field))
  if exclude_cycle:
    self.assertNotIn('cycle_question', draft_contents)

class BaseGrantFilesTestCase(BaseGrantTestCase):
  """ Can handle file uploads too """

  def setUp(self, login):
    super(BaseGrantFilesTestCase, self).setUp(login)
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()

  class Meta:
    abstract = True

@override_settings(MIDDLEWARE_CLASSES = TEST_MIDDLEWARE)
class Register(BaseGrantTestCase):

  url = reverse('sjfnw.grants.views.org_register')
  template_success = 'grants/org_home.html'
  template_error = 'grants/org_login_register.html'

  def setUp(self, *args):
    self.printName()

  def test_valid_registration(self):
    """ All fields provided, neither email nor name match an org in db """
    registration = {
      'email': 'uniquenewyork@gmail.com',
      'password': 'one',
      'passwordtwo': 'one',
      'organization': 'Unique, New York'
      }

    self.assertEqual(0, Organization.objects.filter(name='Unique, New York').count())
    self.assertEqual(0, User.objects.filter(email='uniquenewyork@gmail.com').count())

    response = self.client.post(self.url, registration, follow=True)

    self.assertEqual(1, Organization.objects.filter(name='Unique, New York').count())
    self.assertEqual(1, User.objects.filter(email='uniquenewyork@gmail.com').count())
    self.assertTemplateUsed(response, self.template_success)

  def test_repeat_org_name(self):
    """ Name matches an existing org (email doesn't) """
    registration = {
      'email': 'uniquenewyork@gmail.com',
      'password': 'one',
      'passwordtwo': 'one',
      'organization': 'officemax foundation'
      }

    self.assertEqual(1, Organization.objects.filter(name='OfficeMax Foundation').count())
    self.assertEqual(0, User.objects.filter(email='uniquenewyork@gmail.com').count())

    response = self.client.post(self.url, registration, follow=True)

    self.assertEqual(1, Organization.objects.filter(name='OfficeMax Foundation').count())
    self.assertEqual(0, User.objects.filter(email='uniquenewyork@gmail.com').count())
    self.assertTemplateUsed(response, self.template_error)
    self.assertFormError(response, 'register', None,
        'That organization is already registered. Log in instead.')

  def test_repeat_org_email(self):
    """ Email matches an existing org (name doesn't) """
    registration = {
      'email': 'neworg@gmail.com',
      'password': 'one',
      'passwordtwo': 'one',
      'organization': 'Brand New'
    }

    self.assertEqual(1, Organization.objects.filter(email='neworg@gmail.com').count())
    self.assertEqual(0, Organization.objects.filter(name='Brand New').count())

    response = self.client.post(self.url, registration, follow=True)

    self.assertEqual(1, Organization.objects.filter(email='neworg@gmail.com').count())
    self.assertEqual(0, Organization.objects.filter(name='Brand New').count())
    self.assertTemplateUsed(response, self.template_error)
    self.assertFormError(response, 'register', None,
        'That email is already registered. Log in instead.')

  def test_repeat_user_email(self):
    """ Email matches a user, but email/name don't match an org """
    user = User.objects.create_user('bababa@gmail.com', 'neworg@gmail.com', 'noob')

    registration = {
      'email': 'bababa@gmail.com',
      'password': 'one',
      'passwordtwo': 'one',
      'organization': 'Brand New'
      }

    self.assertEqual(1, User.objects.filter(email='neworg@gmail.com').count())
    self.assertEqual(0, Organization.objects.filter(name='Brand New').count())

    response = self.client.post(self.url, registration, follow=True)

    self.assertEqual(1, User.objects.filter(email='neworg@gmail.com').count())
    self.assertEqual(0, Organization.objects.filter(name='Brand New').count())
    self.assertTemplateUsed(response, self.template_error)
    self.assertFormError(response, 'register', None,
        'That email is registered with Project Central. Please register using a different email.')

  def test_admin_entered_match(self):
    """ Org name matches an org that was entered by staff (no login email) """

    org = Organization(name = "Ye olde Orge")
    org.save()

    registration = {
      'email': 'bababa@gmail.com',
      'password': 'one',
      'passwordtwo': 'one',
      'organization': 'Ye olde Orge'
    }

    response = self.client.post(self.url, registration, follow=True)
    
    org = Organization(name = "Ye olde Orge")
    # org email was updated
    #self.assertEqual(org.email, registration['email'])
    # user was created, is_active = False
    self.assertEqual(1, User.objects.filter(email='bababa@gmail.com', is_active=False).count())
    # stayed on login page
    self.assertTemplateUsed(response, self.template_error)
    # message telling them to contact admin
    self.assertMessage(response, ('You have registered successfully but your '
        'account needs administrator approval. Please contact '
        '<a href="mailto:info@socialjusticefund.org">info@socialjusticefund.org</a>'))

@override_settings(DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage',
    FILE_UPLOAD_HANDLERS = ('django.core.files.uploadhandler.MemoryFileUploadHandler',),
    MIDDLEWARE_CLASSES = TEST_MIDDLEWARE, MEDIA_ROOT = 'media/')
class ApplySuccessful(BaseGrantFilesTestCase):

  def setUp(self, *args):
    super(ApplySuccessful, self).setUp('testy')


  def test_post_valid_app(self):
    """ scenario: start with a complete draft, post to apply
                  general, no fiscal, all-in-one budget

      verify: response is success page
              grantapplication created
              draft deleted
              email sent
              org profile updated """

    org = Organization.objects.get(pk = 2)
    self.assertEqual(0, GrantApplication.objects.filter(organization_id = 2, grant_cycle_id = 3).count())
    draft = DraftGrantApplication.objects.get(organization_id = 2, grant_cycle_id = 3)
    self.assertEqual(org.mission, 'Some crap')

    response = self.client.post('/apply/3/', follow=True)

    #form = response.context['form']
    #print(form.errors)
    org = Organization.objects.get(pk = 2)
    self.assertTemplateUsed(response, 'grants/submitted.html')
    self.assertEqual(org.mission, u'Our mission is to boldly go where no database has gone before.')
    self.assertEqual(1, GrantApplication.objects.filter(organization_id = 2, grant_cycle_id = 3).count())
    self.assertEqual(0, DraftGrantApplication.objects.filter(organization_id = 2, grant_cycle_id = 3).count())

  def test_saved_timeline1(self):

    answers = [ 'Jan', 'Chillin', 'Not applicable',
                '', '', '',
                '', '', '',
                '', '', '',
                '', '', '']

    draft = DraftGrantApplication.objects.get(organization_id = 2, grant_cycle_id = 3)
    alterDraftTimeline(draft, answers)

    response = self.client.post('/apply/3/', follow=True)
    self.assertEqual(response.status_code, 200)
    app = GrantApplication.objects.get(organization_id = 2, grant_cycle_id = 3) #TODO failing here
    self.assertEqual(app.timeline, json.dumps(answers))

  def test_saved_timeline5(self):

    answers = [
      'Jan', 'Chillin', 'Not applicable',
      'Feb', 'Petting dogs', '5 dogs',
      'Mar', 'Planting daffodils', 'Sprouts',
      'July', 'Walking around Greenlake', '9 times',
      'August', 'Reading in the shade', 'No sunburns',]

    draft = DraftGrantApplication.objects.get(organization_id = 2, grant_cycle_id = 3)
    alterDraftTimeline(draft, answers)

    response = self.client.post('/apply/3/', follow=True)
    self.assertEqual(response.status_code, 200)
    app = GrantApplication.objects.get(organization_id = 2, grant_cycle_id = 3)
    self.assertEqual(app.timeline, json.dumps(answers))

  def test_mult_budget(self):
    """ scenario: budget1, budget2

        verify: successful submission
                files match  """

    draft = DraftGrantApplication.objects.get(organization_id = 2, grant_cycle_id = 3)
    files = ['', 'funding_sources.docx', 'diversity.doc', 'budget1.docx', 'budget2.txt', '', '', '']
    alterDraftFiles(draft, files)

    response = self.client.post('/apply/3/', follow=True)

    org = Organization.objects.get(pk=2)
    self.assertTemplateUsed(response, 'grants/submitted.html')
    app = GrantApplication.objects.get(organization_id = 2, grant_cycle_id = 3)
    self.assertEqual(0, DraftGrantApplication.objects.filter(organization_id = 2, grant_cycle_id = 3).count())
    self.assertEqual(app.budget1, files[3])
    self.assertEqual(app.budget2, files[4])
    self.assertEqual(app.budget, '')

@override_settings(MIDDLEWARE_CLASSES = TEST_MIDDLEWARE)
class ApplyBlocked(BaseGrantTestCase):

  def setUp(self, *args):
    super(ApplyBlocked, self).setUp('testy')

  def test_closed_cycle(self):
    response = self.client.get('/apply/3/')
    self.assertTemplateUsed('grants/closed.html')

  def test_already_submitted(self):
    self.assertEqual(0, DraftGrantApplication.objects.filter(organization_id = 2, grant_cycle_id = 1).count())

    response = self.client.get('/apply/1/')

    self.assertTemplateUsed('grants/already-applied.html')
    self.assertEqual(0, DraftGrantApplication.objects.filter(organization_id = 2, grant_cycle_id = 1).count())

  def test_upcoming(self):
    response = self.client.get('/apply/4/')
    self.assertTemplateUsed('grants/closed.html')

  def test_nonexistent(self):
    response = self.client.get('/apply/79/')
    self.assertEqual(404, response.status_code)

@override_settings(MIDDLEWARE_CLASSES = TEST_MIDDLEWARE)
class ApplyValidation(BaseGrantFilesTestCase):
  """TO DO
      fiscal
      collab
      timeline
      files  """

  def setUp(self, *args):
    super(ApplyValidation, self).setUp('testy')

  @override_settings(MEDIA_ROOT = 'media/')
  def test_file_validation_budget(self):
    """ scenario: budget + some other budget files
                  no funding sources

        verify: no submission
                error response  """

    draft = DraftGrantApplication.objects.get(organization_id = 2, grant_cycle_id = 3)
    files = ['budget.docx', 'diversity.doc', '', 'budget1.docx', 'budget2.txt', 'budget3.png', '', '']
    alterDraftFiles(draft, files)
    response = self.client.post('/apply/3/', follow=True)

    self.assertTemplateUsed(response, 'grants/org_app.html')
    self.assertEqual(0, GrantApplication.objects.filter(organization_id = 2, grant_cycle_id = 3).count())
    self.assertEqual(1, DraftGrantApplication.objects.filter(organization_id = 2, grant_cycle_id = 3).count())
    self.assertFormError(response, 'form', 'funding_sources', "This field is required.")
    self.assertFormError(response, 'form', 'budget', '<div class="form_error">Budget documents are required. You may upload them as one file or as multuple files.</div>')

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

    response = self.client.post('/apply/3/', follow=True)

    self.assertTemplateUsed(response, 'grants/org_app.html')
    self.assertEqual(0, GrantApplication.objects.filter(organization_id = 2, grant_cycle_id = 3).count())
    self.assertEqual(1, DraftGrantApplication.objects.filter(organization_id = 2, grant_cycle_id = 3).count())
    self.assertFormError(response, 'form', 'project_title', "This field is required when applying for project support.")
    self.assertFormError(response, 'form', 'project_budget', "This field is required when applying for project support.")

  def test_timeline_validation_incomplete(self):

    draft = DraftGrantApplication.objects.get(organization_id = 2, grant_cycle_id = 3)
    answers = [
      'Jan', 'Chillin', 'Not applicable',
      'Feb', 'Petting dogs', '5 dogs',
      'Mar', '', 'Sprouts',
      'July', '', '',
      '', 'Reading in the shade', 'No sunburns',]
    alterDraftTimeline(draft, answers)

    response = self.client.post('/apply/3/', follow=True)
    self.assertFormError(response, 'form', 'timeline', '<div class="form_error">All three columns are required for each quarter that you include in your timeline.</div>')

  def test_timeline_validation_empty(self):

    draft = DraftGrantApplication.objects.get(organization_id = 2, grant_cycle_id = 3)
    answers = [
      '', '', '',
      '', '', '',
      '', '', '',
      '', '', '',
      '', '', '']
    alterDraftTimeline(draft, answers)

    response = self.client.post('/apply/3/', follow=True)
    self.assertFormError(response, 'form', 'timeline', '<div class="form_error">This field is required.</div>')

@override_settings(MIDDLEWARE_CLASSES = TEST_MIDDLEWARE)
class StartApplication(BaseGrantTestCase): #MIGHT BE OUT OF DATE

  def setUp(self, *args):
    super(StartApplication, self).setUp('none')

  def test_load_first_app(self):
    """ Brand new org starting an application
        Page loads
        Form is blank
        Draft is created """

    self.logInNeworg()
    self.assertEqual(0, DraftGrantApplication.objects.filter(organization_id=1, grant_cycle_id=1).count())

    response = self.client.get('/apply/1/')

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('grants/org_app.html')
    self.assertEqual(1, DraftGrantApplication.objects.filter(organization_id=1, grant_cycle_id=1).count())

  def test_load_second_app(self):
    """ Org with profile starting an application
        Page loads
        Form has stuff from profile
        Draft is created """

    self.logInTestorg()
    self.assertEqual(0, DraftGrantApplication.objects.filter(organization_id=2, grant_cycle_id=5).count())

    response = self.client.get('/apply/5/')

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed('grants/org_app.html')
    org = Organization.objects.get(pk=2)
    self.assertContains(response, org.mission)
    self.assertEqual(1, DraftGrantApplication.objects.filter(organization_id=2, grant_cycle_id=5).count())

@override_settings(MIDDLEWARE_CLASSES = TEST_MIDDLEWARE)
class DraftWarning(BaseGrantTestCase):

  def setUp(self, *args):
    super(DraftWarning, self).setUp('admin')

  def test_long_alert(self):
    """ Cycle created 12 days ago with cycle closing in 7.5 days """

    self.assertEqual(len(mail.outbox), 0)

    now = timezone.now()
    draft = DraftGrantApplication.objects.get(pk=1)
    draft.created = now - datetime.timedelta(days=12)
    draft.save()
    cycle = GrantCycle.objects.get(pk=2)
    cycle.close = now + datetime.timedelta(days=7, hours=12)
    cycle.save()

    response = self.client.get('/mail/drafts/')
    self.assertEqual(len(mail.outbox), 1)

  def test_long_alert_skip(self):
    """ Cycle created now with cycle closing in 7.5 days """

    self.assertEqual(len(mail.outbox), 0)

    now = timezone.now()
    draft = DraftGrantApplication.objects.get(pk=1)
    draft.created = now
    draft.save()
    cycle = GrantCycle.objects.get(pk=2)
    cycle.close = now + datetime.timedelta(days=7, hours=12)
    cycle.save()

    response = self.client.get('/mail/drafts/')
    self.assertEqual(len(mail.outbox), 0)

  def test_short_alert(self):
    """ Cycle created now with cycle closing in 2.5 days """

    self.assertEqual(len(mail.outbox), 0)

    now = timezone.now()
    draft = DraftGrantApplication.objects.get(pk=1)
    draft.created = now
    draft.save()
    cycle = GrantCycle.objects.get(pk=2)
    cycle.close = now + datetime.timedelta(days=2, hours=12)
    cycle.save()

    response = self.client.get('/mail/drafts/')
    self.assertEqual(len(mail.outbox), 1)

  def test_short_alert_ignore(self):
    """ Cycle created 12 days ago with cycle closing in 2.5 days """
    self.assertEqual(len(mail.outbox), 0)

    now = timezone.now()
    draft = DraftGrantApplication.objects.get(pk=1)
    draft.created = now - datetime.timedelta(days=12)
    draft.save()
    cycle = GrantCycle.objects.get(pk=2)
    cycle.close = now + datetime.timedelta(days=2, hours=12)
    cycle.save()

    response = self.client.get('/mail/drafts/')
    self.assertEqual(len(mail.outbox), 0)

@override_settings(MIDDLEWARE_CLASSES = TEST_MIDDLEWARE)
class OrgRollover(BaseGrantTestCase):
  """ Basic success
  content,   timeline,   files,   not extra cycle q   """

  def setUp(self, *args):
    super(OrgRollover, self).setUp('newbie')

  def test_draft_rollover(self):
    """ scenario: take complete draft, make it belong to new org, rollover to cycle 1
        verify:
          success (status code & template)
          new draft created
          new draft contents = old draft contents (ignoring cycle q)
          new draft files = old draft files  """

    draft = DraftGrantApplication.objects.get(organization_id = 2, grant_cycle_id = 3)
    draft.organization = Organization.objects.get(pk=1)
    draft.save()
    self.assertEqual(0, DraftGrantApplication.objects.filter(organization_id=1, grant_cycle_id=1).count())

    response = self.client.post('/apply/copy', {'cycle':'1', 'draft':'2', 'application':''}, follow=True)

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'grants/org_app.html')
    self.assertEqual(1, DraftGrantApplication.objects.filter(organization_id=1, grant_cycle_id=1).count())
    new_draft = DraftGrantApplication.objects.get(organization_id = 1, grant_cycle_id = 1)
    old_contents = json.loads(draft.contents) # TODO could this use the compare function defined in base?
    cq = old_contents.pop('cycle_question', None)
    new_contents = json.loads(new_draft.contents)
    nq = new_contents.pop('cycle_question', '')
    self.assertEqual(old_contents, new_contents)
    self.assertNotEqual(cq, nq)
    for field in GrantApplication.file_fields():
      self.assertEqual(getattr(draft, field), getattr(new_draft, field))

  def test_app_rollover(self):
    """ scenario: take a submitted app, make it belong to new org, rollover to cycle 1
        verify:
          success (status code & template)
          new draft created
          draft contents = app contents (ignoring cycle q)
          draft files = app files  """

    self.assertEqual(0, DraftGrantApplication.objects.filter(organization_id=1, grant_cycle_id=2).count())

    app = GrantApplication.objects.get(organization_id=2, grant_cycle_id=1)
    app.organization = Organization.objects.get(pk=1)
    app.save()

    response = self.client.post('/apply/copy', {'cycle':'2', 'draft':'', 'application':'1'}, follow=True)

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'grants/org_app.html')
    self.assertEqual(1, DraftGrantApplication.objects.filter(organization_id=1, grant_cycle_id=2).count())

    draft = DraftGrantApplication.objects.get(organization_id=1, grant_cycle_id=2)
    assertDraftAppMatch(self, draft, app, True)

  def test_rollover_form_display(self):
    response = self.client.get('/apply/copy')
    self.assertTemplateUsed(response, 'grants/org_app_copy.html')
    self.assertEqual(response.context['apps_count'], 2)
    self.assertEqual(response.context['cycle_count'], 4)
    self.assertNotContains(response, 'Select')

    self.client.logout()
    self.logInTestorg()
    response = self.client.get('/apply/copy')
    self.assertTemplateUsed(response, 'grants/org_app_copy.html')
    self.assertEqual(response.context['apps_count'], 5)
    self.assertEqual(response.context['cycle_count'], 2)
    self.assertContains(response, 'Select')

@override_settings(MIDDLEWARE_CLASSES = TEST_MIDDLEWARE)
class AdminRevert(BaseGrantTestCase):

  def setUp(self, *args):
    super(AdminRevert, self).setUp('admin')

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

    self.assertEqual(0, DraftGrantApplication.objects.filter(organization_id=2, grant_cycle_id=1).count())
    app = GrantApplication.objects.get(organization_id=2, grant_cycle_id=1)

    response = self.client.post('/admin/grants/grantapplication/1/revert')

    self.assertEqual(1, DraftGrantApplication.objects.filter(organization_id=2, grant_cycle_id=1).count())
    draft = DraftGrantApplication.objects.get(organization_id=2, grant_cycle_id=1)
    assertDraftAppMatch(self, draft, app, False)

@unittest.skip('Incomplete')
@override_settings(MIDDLEWARE_CLASSES = TEST_MIDDLEWARE)
class AdminRollover(BaseGrantTestCase):

  def setUp(self, *args):
    super(AdminRevert, self).setUp('admin')

@override_settings(MIDDLEWARE_CLASSES = TEST_MIDDLEWARE)
class DraftExtension(BaseGrantTestCase):

  def setUp(self, *args):
    super(DraftExtension, self).setUp('admin')

  def test_create_draft(self):
    """ Admin create a draft for Fresh New Org """

    self.assertEqual(0, DraftGrantApplication.objects.filter(organization_id=1).count())

    response = self.client.post('/admin/grants/draftgrantapplication/add/',
                                {'organization': '1', 'grant_cycle': '3',
                                 'extended_deadline_0': '2013-04-07',
                                 'extended_deadline_1': '11:19:46'})

    self.assertEqual(response.status_code, 302)
    new = DraftGrantApplication.objects.get(organization_id=1) #in effect, asserts 1 draft
    self.assertTrue(new.editable)
    self.assertIn('/admin/grants/draftgrantapplication/', response.__getitem__('location'), )

  @unittest.skip('Incomplete')
  def test_org_drafts_list(self):
    pass

@override_settings(MIDDLEWARE_CLASSES = TEST_MIDDLEWARE)
class Draft(BaseGrantTestCase):

  def setUp(self, *args):
    super(Draft, self).setUp('testy')

  def test_autosave1(self):
    """ scenario: steal contents of draft 2, turn it into a dict. submit that as request.POST for cycle 5
        verify: draft contents match  """
    complete_draft = DraftGrantApplication.objects.get(pk=2)
    new_draft = DraftGrantApplication(organization = Organization.objects.get(pk=2), grant_cycle = GrantCycle.objects.get(pk=5))
    new_draft.save()
    dic = json.loads(complete_draft.contents)
    #fake a user id like the js would normally do
    dic['user_id'] = 'asdFDHAF34qqhRHFEA'
    self.maxDiff = None

    response = self.client.post('/apply/5/autosave/', dic)
    self.assertEqual(200, response.status_code)
    new_draft = DraftGrantApplication.objects.get(organization_id=2, grant_cycle_id=5)
    new_c = json.loads(new_draft.contents)
    del new_c['user_id']
    self.assertEqual(json.loads(complete_draft.contents), new_c)

@override_settings(MIDDLEWARE_CLASSES = TEST_MIDDLEWARE)
class ViewGrantPermissions(BaseGrantTestCase):

  fixtures = ['sjfnw/grants/fixtures/test_grants.json', 'sjfnw/fund/fixtures/test_fund.json']

  def setUp(self, *args):
    self.printName()
    app = GrantApplication.objects.get(pk=1)
    app.giving_project = GivingProject.objects.get(pk=2)
    app.save()

  """ Note: using grant app #1
    Author: testorg@gmail.com (org #2)
    GP: #2, which newacct is a member of, test is not  
  """
  def test_author(self):
    self.logInTestorg()

    response = self.client.get('/grants/view/1', follow=True)

    self.assertTemplateUsed(response, 'grants/reading.html')
    self.assertEqual(3, response.context['perm'])

  def test_other_org(self):
    self.logInNeworg()

    response = self.client.get('/grants/view/1', follow=True)

    self.assertTemplateUsed(response, 'grants/reading.html')
    self.assertEqual(0, response.context['perm'])

  def test_staff(self):
    self.logInAdmin()

    response = self.client.get('/grants/view/1', follow=True)

    self.assertTemplateUsed(response, 'grants/reading.html')
    self.assertEqual(2, response.context['perm'])

  def test_valid_member(self):
    self.logInNewbie()

    response = self.client.get('/grants/view/1', follow=True)

    self.assertTemplateUsed(response, 'grants/reading.html')
    self.assertEqual(1, response.context['perm'])

  def test_invalid_member(self):
    self.logInTesty()

    response = self.client.get('/grants/view/1', follow=True)

    self.assertTemplateUsed(response, 'grants/reading.html')
    self.assertEqual(0, response.context['perm'])

@override_settings(MIDDLEWARE_CLASSES = TEST_MIDDLEWARE)
class OrgHomeAwards(BaseGrantTestCase):

  url = reverse('sjfnw.grants.views.org_home')
  template = 'grants/org_home.html'

  def setUp(self):
    super(OrgHomeAwards, self).setUp('testy')

  def test_none(self):
    """ org has no awards. verify no award info is shown """
    
    response = self.client.get(self.url)

    self.assertTemplateUsed(self.template)
    self.assertNotContains(response, 'Agreement mailed')

  def test_early(self):
    """ org has an award, but agreement has not been mailed. verify not shown """
    award = GrantAward(application_id = 1, amount = 9000)
    award.save()

    response = self.client.get(self.url)

    self.assertTemplateUsed(self.template)
    self.assertNotContains(response, 'Agreement mailed')

  def test_sent(self):
    """ org has award, agreement mailed. verify shown """
    award = GrantAward(application_id = 1, amount = 9000,
        agreement_mailed = timezone.now()-datetime.timedelta(days=1))
    award.save()

    response = self.client.get(self.url)

    self.assertTemplateUsed(self.template)
    self.assertContains(response, 'Agreement mailed')

