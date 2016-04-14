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
    self.log_in_admin()

  def test_create_draft(self):
    """ Admin create a draft for Fresh New Org """

    self.assertEqual(0, models.DraftGrantApplication.objects.filter(organization_id=1).count())

    response = self.client.post('/admin/grants/draftgrantapplication/add/', {
      'organization': '1', 'grant_cycle': '3', 'extended_deadline_0': '2013-04-07',
      'extended_deadline_1': '11:19:46'
    })

    self.assertEqual(response.status_code, 302)
    new = models.DraftGrantApplication.objects.get(organization_id=1)
    self.assertTrue(new.editable)
    self.assertIn('/admin/grants/draftgrantapplication/', response.__getitem__('location'))


class Draft(BaseGrantTestCase):

  def setUp(self):
    super(Draft, self).setUp()
    self.log_in_test_org()

  def test_autosave1(self):
    complete_draft = models.DraftGrantApplication.objects.get(pk=2)
    new_draft = models.DraftGrantApplication(
      organization=models.Organization.objects.get(pk=2),
      grant_cycle=models.GrantCycle.objects.get(pk=5)
    )
    new_draft.save()
    dic = json.loads(complete_draft.contents)
    # fake a user id like the js would normally do
    dic['user_id'] = 'asdFDHAF34qqhRHFEA'
    self.maxDiff = None # pylint: disable=invalid-name

    response = self.client.post('/apply/5/autosave/', dic)
    self.assertEqual(200, response.status_code)
    new_draft = models.DraftGrantApplication.objects.get(organization_id=2, grant_cycle_id=5)
    new_c = json.loads(new_draft.contents)
    del new_c['user_id']
    self.assertEqual(json.loads(complete_draft.contents), new_c)


class DraftWarning(BaseGrantTestCase):

  def setUp(self):
    super(DraftWarning, self).setUp()
    self.log_in_admin()

  def test_long_alert(self):
    """ Cycle created 12 days ago with cycle closing in 7.5 days
    Expect email to be sent """

    self.assertEqual(len(mail.outbox), 0)

    now = timezone.now()
    draft = models.DraftGrantApplication.objects.get(pk=2)
    draft.created = now - timedelta(days=12)
    draft.save()
    cycle = models.GrantCycle.objects.get(pk=2)
    cycle.close = now + timedelta(days=7, hours=12)
    cycle.save()

    self.client.get('/mail/drafts/')
    self.assertEqual(len(mail.outbox), 1)

  def test_long_alert_skip(self):
    """ Cycle created now with cycle closing in 7.5 days
    Expect email to not be sent """

    self.assertEqual(len(mail.outbox), 0)

    now = timezone.now()
    draft = models.DraftGrantApplication.objects.get(pk=2)
    draft.created = now
    draft.save()
    cycle = models.GrantCycle.objects.get(pk=2)
    cycle.close = now + timedelta(days=7, hours=12)
    cycle.save()

    self.client.get('/mail/drafts/')
    self.assertEqual(len(mail.outbox), 0)

  def test_short_alert(self):
    """ Cycle created now with cycle closing in 2.5 days """

    self.assertEqual(len(mail.outbox), 0)

    now = timezone.now()
    draft = models.DraftGrantApplication.objects.get(pk=2)
    draft.created = now
    draft.save()
    cycle = models.GrantCycle.objects.get(pk=2)
    cycle.close = now + timedelta(days=2, hours=12)
    cycle.save()

    self.client.get('/mail/drafts/')
    self.assertEqual(len(mail.outbox), 1)

  def test_short_alert_ignore(self):
    """ Cycle created 12 days ago with cycle closing in 2.5 days """
    self.assertEqual(len(mail.outbox), 0)

    now = timezone.now()
    draft = models.DraftGrantApplication.objects.get(pk=2)
    draft.created = now - timedelta(days=12)
    draft.save()
    cycle = models.GrantCycle.objects.get(pk=2)
    cycle.close = now + timedelta(days=2, hours=12)
    cycle.save()

    self.client.get('/mail/drafts/')
    self.assertEqual(len(mail.outbox), 0)


class DiscardDraft(BaseGrantTestCase):

  url = reverse('sjfnw.grants.views.discard_draft', kwargs={'draft_id': 1})

  def setUp(self):
    super(DiscardDraft, self).setUp()
    self.log_in_test_org()

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
