from datetime import timedelta
import json
import logging

from django.core import mail
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.utils import timezone

from sjfnw.grants import models
from sjfnw.grants.tests.base import BaseGrantTestCase
from sjfnw.grants.tests.test_apply import BaseGrantFilesTestCase

logger = logging.getLogger('sjfnw')

def _get_autosave_url(award_id):
  return reverse('sjfnw.grants.views.autosave_yer', kwargs={'award_id': award_id})

def _get_yer_url(award_id):
  return reverse('sjfnw.grants.views.year_end_report', kwargs={'award_id': award_id})

@override_settings(MEDIA_ROOT='sjfnw/grants/tests/media/',
    DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage',
    FILE_UPLOAD_HANDLERS=('django.core.files.uploadhandler.MemoryFileUploadHandler',))
class YearEndReportForm(BaseGrantFilesTestCase):

  def setUp(self):
    super(YearEndReportForm, self).setUp()
    self.log_in_test_org()
    today = timezone.now()
    award = models.GivingProjectGrant(
        projectapp_id=1,
        amount=5000,
        agreement_mailed=today - timedelta(days=345),
        agreement_returned=today - timedelta(days=350),
        first_yer_due=today + timedelta(days=9))
    award.save()
    self.award_id = award.pk

  def test_home_link(self):
    response = self.client.get('/apply/')

    self.assertTemplateUsed('grants/org_home.html')
    self.assertContains(response, '<a href="/report/%d">' % self.award_id)

  def test_home_link_early(self):
    """ Link to report is shown even if agreement hasn't been mailed """

    award = models.GivingProjectGrant.objects.get(pk=self.award_id)
    award.agreement_mailed = None
    award.save()

    response = self.client.get('/apply/')

    self.assertTemplateUsed('grants/org_home.html')
    self.assertContains(response, '<a href="/report/%d">' % self.award_id)

  def test_late_home_link(self):
    """ Link to report is shown even if due date has passed """

    award = models.GivingProjectGrant.objects.get(pk=self.award_id)
    award.first_yer_due = timezone.now() - timedelta(days=4)
    award.save()

    response = self.client.get('/apply/')

    self.assertTemplateUsed('grants/org_home.html')
    self.assertContains(response, '<a href="/report/%d">' % self.award_id)

  def test_second_home_link(self):
    # submit first YER
    self.test_valid_stay_informed()

    # make award be two-year
    award = models.GivingProjectGrant.objects.get(pk=self.award_id)
    award.second_amount = 5000
    award.agreement_mailed = timezone.now() - timedelta(weeks=102)
    award.save()

    response = self.client.get('/apply/')

    self.assertTemplateUsed('grants/org_home.html')
    self.assertContains(response, 'Year end report</a> submitted', count=1)
    self.assertContains(response, '<a href="/report/%d">' % self.award_id, count=1)

  def test_no_second_home_link(self):

    # make award be two-year
    award = models.GivingProjectGrant.objects.get(pk=self.award_id)
    award.second_amount = 5000
    award.first_yer_due = timezone.now() - timedelta(weeks=1)
    award.save()

    # re-fetch to get updated version with fields that change during save
    award = models.GivingProjectGrant.objects.get(pk=self.award_id)

    # verify that only first due date/link shows
    response = self.client.get('/apply/')
    self.assertTemplateUsed('grants/org_home.html')
    self.assertContains(response, '<a href="/report/%d">' % self.award_id, count=1)
    self.assertContains(response, 'due {:%-m/%-d/%y}'.format(award.first_yer_due), count=1)

  def test_two_completed(self):
    # submit first YER
    self.test_valid_stay_informed()

    # make award be two-year
    award = models.GivingProjectGrant.objects.get(pk=self.award_id)
    award.second_amount = 5000
    award.agreement_mailed = timezone.now() - timedelta(weeks=102)
    award.save()

    response = self.client.get('/apply/')

    self.assertTemplateUsed('grants/org_home.html')
    self.assertContains(response, 'Year end report</a> submitted', count=1)
    self.assertContains(response, '<a href="/report/%d">' % self.award_id, count=1)

    # submit second YER
    self.test_valid_stay_informed()

    response = self.client.get('/apply/')

    self.assertTemplateUsed('grants/org_home.html')
    self.assertContains(response, 'Year end report</a> submitted', count=2)
    self.assertNotContains(response, '<a href="/report/%d">' % self.award_id)

  def _create_draft(self):
    """ Not a test. Used by other tests to set up a draft """

    draft_count = models.YERDraft.objects.filter(award_id=self.award_id).count()
    response = self.client.get(_get_yer_url(self.award_id))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'grants/yer_form.html')
    self.assertEqual(models.YERDraft.objects.filter(award_id=self.award_id).count(), draft_count+1)

  def test_start_report(self):
    award = models.GivingProjectGrant.objects.get(pk=self.award_id)
    mailed = award.agreement_mailed

    response = self.client.get(_get_yer_url(self.award_id))
    self.assertTemplateUsed(response, 'grants/yer_form.html')

    form = response.context['form']
    application = models.GrantApplication.objects.get(pk=1) # fixture

    # assert website autofilled from app
    self.assertEqual(form['website'].value(), application.website)
    expected_title = 'Year-end Report for {:%b %d, %Y} - {:%b %d, %Y}'.format(
        mailed.replace(year=mailed.year), mailed.replace(year=mailed.year+1))
    self.assertContains(response, expected_title)

  def test_start_second_report(self):
    # submit first YER
    self.test_valid_stay_informed()

    # make award be two-year
    award = models.GivingProjectGrant.objects.get(pk=self.award_id)
    award.second_amount = 3000
    award.agreement_mailed = timezone.now() - timedelta(weeks=102)
    award.save()
    award = models.GivingProjectGrant.objects.get(pk=self.award_id)

    self.assertEqual(0, models.YERDraft.objects.filter(award_id=self.award_id).count())

    response = self.client.get(_get_yer_url(self.award_id))

    self.assertTemplateUsed(response, 'grants/yer_form.html')
    mailed = award.agreement_mailed
    expected_title = 'Year-end Report for {:%b %d, %Y} - {:%b %d, %Y}'.format(
        mailed.replace(year=mailed.year+1), mailed.replace(year=mailed.year+2))
    self.assertContains(response, expected_title)

    application = models.GrantApplication.objects.get(pk=1)
    self.assertEqual(response.context['form']['website'].value(), application.website)
    self.assertEqual(1, models.YERDraft.objects.filter(award_id=self.award_id).count())

  def test_autosave(self):
    self._create_draft()

    post_data = {
      'summarize_last_year': 'We did soooooo much stuff last year!!',
      'goal_progress': 'What are goals?',
      'total_size': '546 or 547',
      'other_comments': 'All my single ladies'
    }

    response = self.client.post(_get_autosave_url(self.award_id), post_data)
    self.assertEqual(200, response.status_code)
    draft = models.YERDraft.objects.get(award_id=self.award_id)
    self.assertEqual(json.loads(draft.contents), post_data)

  def test_valid_stay_informed(self):
    self._create_draft()

    post_data = {
      'other_comments': 'Some comments',
      'total_size': '500',
      'award': '55',
      'quantitative_measures': 'Measures',
      'major_changes': 'Changes',
      'summarize_last_year': 'It was all right.',
      'other': '',
      'evaluation': 'abc',
      'donations_count': '503',
      'donations_count_prev': '50',
      'collaboration': 'der',
      'user_id': '',
      'phone': '208-861-8907',
      'goal_progress': 'We haven\'t made much progress sorry.',
      'contact_person_1': 'Executive Board Co-Chair',
      'contact_person_0': 'Kria Pry',
      'new_funding': 'None! UGH.',
      'email': 'Idahoc@gmail.com',
      'facebook': '',
      'website': 'www.idossc.org',
      'achieved': 'Achievement awards.',
      'listserve': 'yes yes',
      'stay_informed': '{}'
    }

    # autosave the post_data (page js does that prior to submitting)
    response = self.client.post(_get_autosave_url(self.award_id), post_data)
    self.assertEqual(200, response.status_code)

    # confirm draft updated
    draft = models.YERDraft.objects.get(award_id=self.award_id)
    self.assertEqual(json.loads(draft.contents), post_data)

    # add files to draft
    draft.photo1 = 'budget3.png'
    draft.photo2 = 'budget3.png'
    draft.photo_release = 'budget1.docx'
    draft.save()

    # get number of existing yer for award
    yer_count = models.YearEndReport.objects.filter(award_id=self.award_id).count()
    mail_count = len(mail.outbox)

    # submit
    response = self.client.post(_get_yer_url(self.award_id))

    self.assertTemplateUsed('grants/yer_submitted.html')

    # verify report matches draft
    yer = models.YearEndReport.objects.filter(award_id=self.award_id)

    self.assertEqual(len(yer), yer_count+1)
    yer = yer[yer_count]

    self.assertEqual(yer.photo1, draft.photo1)
    self.assertEqual(yer.photo2, draft.photo2)
    self.assertEqual(yer.photo_release, draft.photo_release)

    self.assertEqual(len(mail.outbox), mail_count+1)
    email = mail.outbox[mail_count]
    self.assertEqual(email.subject, 'Year end report submitted')
    self.assertEqual(email.to, [yer.email])

  def test_valid_late(self):
    """ Run the valid test but with a YER that is overdue """

    award = models.GivingProjectGrant.objects.get(pk=self.award_id)
    award.agreement_mailed = timezone.now() - timedelta(days=400)
    award.save()

    self.test_valid_stay_informed()

  def test_start_late(self):
    """ Run the start draft test but with a YER that is overdue """
    award = models.GivingProjectGrant.objects.get(pk=self.award_id)
    award.agreement_mailed = timezone.now() - timedelta(days=400)
    award.save()

    self.test_start_report()


class YearEndReportReminders(BaseGrantTestCase):

  projectapp_id = 1
  url = reverse('sjfnw.grants.cron.yer_reminder_email')

  def setUp(self):
    super(YearEndReportReminders, self).setUp()
    self.log_in_admin()

  def test_two_months_prior(self):
    """ Verify reminder is not sent 2 months before report is due """

    # create award where yer should be due in 60 days
    today = timezone.now().date()
    award = models.GivingProjectGrant(projectapp_id=1, amount=5000,
                                      first_yer_due=today + timedelta(days=60))
    award.save()

    # verify that yer is due in 60 days
    self.assertEqual(award.next_yer_due(), today + timedelta(days=60))

    # verify that email is not sent
    self.assertEqual(len(mail.outbox), 0)
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(mail.outbox), 0)

  def test_first_email(self):
    """ Verify that reminder email gets sent 30 days prior to due date """

    # create award where yer should be due in 30 days
    today = timezone.now().date()
    award = models.GivingProjectGrant(projectapp_id=1, amount=5000,
                                      first_yer_due=today + timedelta(days=30))
    award.save()

    # verify that yer is due in 30 days
    self.assertEqual(award.next_yer_due(), today + timedelta(days=30))

    # verify that email is not sent
    self.assertEqual(len(mail.outbox), 0)
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(mail.outbox), 1)

  def test_15_days_prior(self):
    """ Verify that no email is sent 15 days prior to due date """

    # create award where yer should be due in 15 days
    today = timezone.now().date()
    award = models.GivingProjectGrant(projectapp_id=1, amount=5000,
                                      first_yer_due=today + timedelta(days=15))
    award.save()

    # verify that yer is due in 15 days
    self.assertEqual(award.next_yer_due(), today + timedelta(days=15))

    # verify that email is not sent
    self.assertEqual(len(mail.outbox), 0)
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(mail.outbox), 0)

  def test_second_email(self):
    """ Verify that a reminder email goes out 7 days prior to due date """

    # create award where yer should be due in 7 days
    today = timezone.now().date()
    award = models.GivingProjectGrant(projectapp_id=1, amount=5000,
                                      first_yer_due=today + timedelta(days=7))
    award.save()

    # verify that yer is due in 7 days
    self.assertEqual(award.next_yer_due(), today + timedelta(days=7))

    # verify that email is sent
    self.assertEqual(len(mail.outbox), 0)
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(mail.outbox), 1)

  def test_yer_complete(self):
    """ Verify that an email is not sent if a year-end report has been completed """

    # create award where yer should be due in 7 days
    today = timezone.now().date()
    award = models.GivingProjectGrant(projectapp_id=1, amount=5000,
                                      first_yer_due=today + timedelta(days=7))
    award.save()

    # verify that YER is due in 7 days
    self.assertEqual(award.next_yer_due(), today + timedelta(days=7))

    # create YER
    yer = models.YearEndReport(award=award, total_size=10, donations_count=50)
    yer.save()

    # verify that no more are due
    self.assertEqual(award.next_yer_due(), None)

    # verify that email is not sent
    self.assertEqual(len(mail.outbox), 0)
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(mail.outbox), 0)

  def test_second_yer_reminder(self):
    """ Verify that reminder email is sent if second year end report due"""

    today = timezone.now().date()
    first_yer_due = (today + timedelta(days=7)).replace(year=today.year-1)
    award = models.GivingProjectGrant(
        projectapp_id=1, amount=5000, second_amount=5000,
        first_yer_due=first_yer_due, second_check_mailed=today
    )
    award.save()

    self.assertEqual(award.next_yer_due(), award.first_yer_due)

    # submit first YER
    yer = models.YearEndReport(award=award, submitted=first_yer_due,
                               total_size=10, donations_count=50)
    yer.save()

    # verify that second yer is due in 7 days
    self.assertEqual(award.next_yer_due(), today + timedelta(days=7))

    # verify that email is sent
    self.assertEqual(len(mail.outbox), 0)
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(mail.outbox), 1)

  def test_second_yer_complete(self):
    """ Verify that reminder email is not sent if second year end report completed"""

    today = timezone.now().date()
    first_yer_due = (today + timedelta(days=7)).replace(year=today.year-1)
    award = models.GivingProjectGrant(
          projectapp_id=1, amount=5000, second_amount=5000,
          first_yer_due=first_yer_due, second_check_mailed=today
    )
    award.save()

    # create first YER
    yer = models.YearEndReport(award=award, total_size=10,
                               submitted=first_yer_due, donations_count=50)
    yer.save()

    self.assertEqual(award.next_yer_due(), award.first_yer_due.replace(year = first_yer_due.year + 1))

    # create second YER
    second_yer = models.YearEndReport(
        award=award, total_size=10, donations_count=50,
        submitted=first_yer_due.replace(year=first_yer_due.year + 1))
    second_yer.save()

    # verify that no YER is due
    self.assertEqual(award.next_yer_due(), None)

    # verify that email is not sent
    self.assertEqual(len(mail.outbox), 0)
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(mail.outbox), 0)


class RolloverYER(BaseGrantTestCase):
  """ Test display and function of the rollover feature for YER """

  url = reverse('sjfnw.grants.views.rollover_yer')

  def setUp(self):
    super(RolloverYER, self).setUp()
    self.log_in_test_org()

  def create_yer(self, award_id):
    yer = models.YearEndReport(award_id=award_id, total_size=10,
                               donations_count=50, contact_person='Name, Position')
    yer.save()

  def test_rollover_link(self):
    """ Verify that link shows on home page """

    response = self.client.get('/apply', follow=True)
    self.assertContains(response, 'rollover a year-end report')

  def test_display_no_awards(self):
    """ Verify correct error msg, no form, if org has no grants """

    self.log_in_new_org()
    response = self.client.get(self.url, follow=True)
    self.assertEqual(response.context['error_msg'],
        'You don\'t have any submitted reports to copy.')

  def test_display_no_reports(self):
    """ Verify error msg, no form if org has grant(s) but no reports """

    award = models.GivingProjectGrant(projectapp_id=1, amount=8000, first_yer_due=timezone.now())
    award.save()
    self.assertNotEqual(models.GivingProjectGrant.objects.filter(
      projectapp__application__organization_id=2).count(), 0)

    response = self.client.get(self.url, follow=True)
    self.assertEqual(response.context['error_msg'],
        'You don\'t have any submitted reports to copy.')

  def test_display_all_reports_done(self):
    """ Verify error msg, no form if org has reports for all grants """
    award = models.GivingProjectGrant(projectapp_id=1, amount=5000, first_yer_due=timezone.now())
    award.save()
    self.create_yer(award.pk)

    response = self.client.get(self.url, follow=True)
    self.assertRegexpMatches(response.context['error_msg'],
        'You have a submitted or draft year-end report for all of your grants')

  def test_display_second_year_missing(self):
    """ Verify form if org has completed one but not both reports for their grant """
    award = models.GivingProjectGrant(projectapp_id=1, amount=5000,
        second_amount=1000, first_yer_due=timezone.now())
    award.save()
    self.create_yer(award.pk)

    response = self.client.get(self.url, follow=True)
    self.assertContains(response, 'option value', count=4)
    self.assertContains(response, 'This form lets you')

  def test_display_form(self):
    """ Verify display of form when there is a valid rollover option """

    # create award and YER
    award = models.GivingProjectGrant(projectapp_id=1, amount=5000, first_yer_due=timezone.now())
    award.save()
    self.create_yer(award.pk)

    # create 2nd award without YER
    papp = models.ProjectApp(application_id=2, giving_project_id=3)
    papp.save()
    mailed = timezone.now() - timedelta(days=355)
    award = models.GivingProjectGrant(projectapp=papp, amount=8000,
        agreement_mailed=mailed, agreement_returned=mailed + timedelta(days=3),
        first_yer_due=timezone.now())
    award.save()

    response = self.client.get(self.url, follow=True)
    self.assertContains(response, 'option value', count=4)
    self.assertContains(response, 'This form lets you')

  def test_submit(self):
    """ Verify that rollover submit works:
      New draft is created for the selected award
      User is redirected to edit draft """

    # set up existing report + award without report
    self.test_display_form()

    award = models.GivingProjectGrant.objects.get(projectapp_id=1)
    award2 = models.GivingProjectGrant.objects.get(projectapp_id=2)
    report = models.YearEndReport.objects.get(award=award)
    self.assertEqual(0, models.YERDraft.objects.filter(award=award2).count())

    post_data = {
      'report': report.pk,
      'award': award2.pk
    }

    response = self.client.post(self.url, post_data, follow=True)

    self.assertTemplateUsed(response, 'grants/yer_form.html')
    self.assertEqual(1, models.YERDraft.objects.filter(award=award2).count())
