from datetime import timedelta
import json, logging

from django.core import mail
from django.core.urlresolvers import reverse
from django.utils import timezone

from sjfnw.grants.tests.base import BaseGrantTestCase
from sjfnw.grants import models

logger = logging.getLogger('sjfnw')

class DraftExtension(BaseGrantTestCase):

  def setUp(self):
    super(DraftExtension, self).setUp()
    self.login_as_admin()

  def test_create_draft(self):
    """ Admin create a draft for Fresh New Org """

    self.assert_count(models.DraftGrantApplication.objects.filter(organization_id=1), 0)

    response = self.client.post('/admin/grants/draftgrantapplication/add/', {
      'organization': '1', 'grant_cycle': '3', 'extended_deadline_0': '2013-04-07',
      'extended_deadline_1': '11:19:46'
    })

    self.assertEqual(response.status_code, 302)
    new = models.DraftGrantApplication.objects.get(organization_id=1)
    self.assertTrue(new.editable)
    self.assertIn('/admin/grants/draftgrantapplication/', response.__getitem__('location'))


class DraftAutosave(BaseGrantTestCase):

  def setUp(self):
    super(DraftAutosave, self).setUp()
    self.login_as_org('test')
    self.cycle_id = 5
    self.url = reverse('sjfnw.grants.views.autosave_app',
                       kwargs={'cycle_id': self.cycle_id})

    new_draft = models.DraftGrantApplication(
        organization_id=self.org_id, grant_cycle_id=self.cycle_id
    )
    new_draft.save()
    self.draft_id = new_draft.pk

  def test_valid(self):
    # borrow contents from an existing draft
    complete_draft = models.DraftGrantApplication.objects.get(pk=2)
    post_data = json.loads(complete_draft.contents)

    response = self.client.post(self.url, post_data)
    self.assertEqual(200, response.status_code)

    new_draft = models.DraftGrantApplication.objects.get(pk=self.draft_id)
    new_c = json.loads(new_draft.contents)
    self.assertEqual(json.loads(complete_draft.contents), new_c)

  def test_not_logged_in(self):
    response = self.client.post(self.url, {'mission': 'Something'})
    self.assertEqual(200, response.status_code)

    self.client.logout()

    response = self.client.post(self.url, {'mission': 'Something'})
    self.assertEqual(401, response.status_code)


class DraftWarning(BaseGrantTestCase):

  def setUp(self):
    super(DraftWarning, self).setUp()
    self.login_as_admin()

  def test_long_alert(self):
    """ Cycle created 12 days ago with cycle closing in 7.5 days
    Expect email to be sent """

    self.assert_length(mail.outbox, 0)

    now = timezone.now()
    draft = models.DraftGrantApplication.objects.get(pk=2)
    draft.created = now - timedelta(days=12)
    draft.save()
    cycle = models.GrantCycle.objects.get(pk=2)
    cycle.close = now + timedelta(days=7, hours=12)
    cycle.save()

    self.client.get('/mail/drafts/')
    self.assert_length(mail.outbox, 1)

  def test_long_alert_skip(self):
    """ Cycle created now with cycle closing in 7.5 days
    Expect email to not be sent """

    self.assert_length(mail.outbox, 0)

    now = timezone.now()
    draft = models.DraftGrantApplication.objects.get(pk=2)
    draft.created = now
    draft.save()
    cycle = models.GrantCycle.objects.get(pk=2)
    cycle.close = now + timedelta(days=7, hours=12)
    cycle.save()

    self.client.get('/mail/drafts/')
    self.assert_length(mail.outbox, 0)

  def test_short_alert(self):
    """ Cycle created now with cycle closing in 2.5 days """

    self.assert_length(mail.outbox, 0)

    now = timezone.now()
    draft = models.DraftGrantApplication.objects.get(pk=2)
    draft.created = now
    draft.save()
    cycle = models.GrantCycle.objects.get(pk=2)
    cycle.close = now + timedelta(days=2, hours=12)
    cycle.save()

    self.client.get('/mail/drafts/')
    self.assert_length(mail.outbox, 1)

  def test_short_alert_ignore(self):
    """ Cycle created 12 days ago with cycle closing in 2.5 days """
    self.assert_length(mail.outbox, 0)

    now = timezone.now()
    draft = models.DraftGrantApplication.objects.get(pk=2)
    draft.created = now - timedelta(days=12)
    draft.save()
    cycle = models.GrantCycle.objects.get(pk=2)
    cycle.close = now + timedelta(days=2, hours=12)
    cycle.save()

    self.client.get('/mail/drafts/')
    self.assert_length(mail.outbox, 0)


class DiscardDraft(BaseGrantTestCase):

  url = reverse('sjfnw.grants.views.discard_draft', kwargs={'draft_id': 1})

  def setUp(self):
    super(DiscardDraft, self).setUp()
    self.login_as_org('test')

  def test_post(self):
    self.assertEqual(models.DraftGrantApplication.objects.filter(pk=1).count(), 1)

    response = self.client.post(self.url)

    self.assertEqual(response.status_code, 405)
    self.assertEqual(response.get('Allow'), 'DELETE')
    self.assertEqual(models.DraftGrantApplication.objects.filter(pk=1).count(), 1)

  def test_valid_delete(self):
    self.assertEqual(models.DraftGrantApplication.objects.filter(pk=1).count(), 1)

    response = self.client.delete(self.url)

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.content, 'success')
    self.assertEqual(models.DraftGrantApplication.objects.filter(pk=1).count(), 0)

  def test_draft_not_found(self):
    self.assertEqual(models.DraftGrantApplication.objects.filter(pk=84).count(), 0)

    response = self.client.delete(
      reverse('sjfnw.grants.views.discard_draft', kwargs={'draft_id': 84})
    )
    self.assertEqual(response.status_code, 404)
    self.assertEqual(response.content, '')

  def test_wrong_org(self):
    draft = models.DraftGrantApplication.objects.get(pk=1)
    draft.organization_id = 1 # it was 2
    draft.save()

    response = self.client.delete(self.url)
    self.assertEqual(response.status_code, 400)
    self.assertEqual(response.content, 'User does not have permission to delete this draft')

class DraftRemoveFile(BaseGrantTestCase):

  def test_unknown_draft_type(self):

    url = reverse('sjfnw.grants.views.remove_file', kwargs={
      'draft_type': 'madeup', 'draft_id': '4', 'file_field': 'budget'
    })

    res = self.client.get(url, follow=True)

    self.assertEqual(res.status_code, 400)

  def test_obj_not_found(self):

    url = reverse('sjfnw.grants.views.remove_file', kwargs={
      'draft_type': 'apply', 'draft_id': '1880', 'file_field': 'budget'
    })

    res = self.client.get(url, follow=True)

    self.assertEqual(res.status_code, 404)

  def test_unknown_field(self):

    url = reverse('sjfnw.grants.views.remove_file', kwargs={
      'draft_type': 'apply', 'draft_id': '1', 'file_field': 'madeup'
    })

    modified = models.DraftGrantApplication.objects.get(pk=1).modified

    res = self.client.get(url, follow=True)

    self.assertEqual(res.status_code, 200)
    modified_after = models.DraftGrantApplication.objects.get(pk=1).modified
    self.assertEqual(modified, modified_after)

  def test_remove_draft_app_file(self):

    url = reverse('sjfnw.grants.views.remove_file', kwargs={
      'draft_type': 'apply', 'draft_id': '2', 'file_field': 'budget1'
    })

    draft = models.DraftGrantApplication.objects.get(pk=2)
    self.assertTrue(draft.budget1)
    self.assertEqual(draft.budget1.name, 'budget1.docx')

    res = self.client.get(url, follow=True)

    self.assertEqual(res.status_code, 200)

    draft = models.DraftGrantApplication.objects.get(pk=2)
    self.assertFalse(draft.budget1)
    self.assertEqual(draft.budget1.name, '')

  def test_remove_draft_yer_file(self):

    # create YER draft, which requires creating an award
    award = models.GivingProjectGrant(projectapp_id=1, amount=10000, first_yer_due='2016-01-01')
    award.save()
    yer_draft = models.YERDraft(award_id=award.pk, photo_release='cats.jpg')
    yer_draft.save()

    draft = models.YERDraft.objects.get(pk=yer_draft.pk)
    self.assertTrue(draft.photo_release)
    self.assertEqual(draft.photo_release.name, 'cats.jpg')

    url = reverse('sjfnw.grants.views.remove_file', kwargs={
      'draft_type': 'report', 'draft_id': yer_draft.pk, 'file_field': 'photo_release'
    })
    res = self.client.get(url, follow=True)

    self.assertEqual(res.status_code, 200)

    draft = models.YERDraft.objects.get(pk=yer_draft.pk)
    self.assertFalse(draft.photo_release)
    self.assertEqual(draft.photo_release.name, '')
