from datetime import timedelta

from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.utils import timezone

from sjfnw.constants import TEST_MIDDLEWARE
from sjfnw.fund import models
from sjfnw.fund.tests.base import BaseFundTestCase, TEST_FIXTURE

import logging, json
logger = logging.getLogger('sjfnw')

@override_settings(MIDDLEWARE_CLASSES = TEST_MIDDLEWARE,
    PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',))
class GPSurveys(BaseFundTestCase):
  """ Test GP eval surveys creation, display, responses """

  fixtures = TEST_FIXTURE
  url = reverse('sjfnw.fund.views.home')
  template = 'fund/fill_gp_survey.html'

  def setUp(self):
    super(GPSurveys, self).setUp()

  def test_creation(self):
    """ Create a survey, verify basic display

    Setup:
      Logged in to admin site
      Submit form data for survey creation in basic querydict format
    """

    # Create form through admin site
    self.log_in_admin()
    form_data = {
     'title': 'Another Survey',
     'intro': 'Please fill this out!',
     'questions_0': 'What is love?',
     'questions_1': 'Baby don\'t',
     'questions_2': 'No more',
     'questions_3': '',
     'questions_4': '',
     'questions_5': '',
     'questions_6': 'What\'s love got to do with it?',
     'questions_7': '',
     'questions_8': '',
     'questions_9': '',
     'questions_10': '',
     'questions_11': '' }
    response = self.client.post('/admin/fund/survey/add/', form_data)

    # Verify it was created
    survey = models.Survey.objects.get(title='Another Survey')
    self.assertEqual(survey.intro, 'Please fill this out!')

    # Connect it to GP1, log into PC and verify it is displaying as expected
    gp_survey = models.GPSurvey(survey=survey, giving_project_id=1, date=timezone.now())
    gp_survey.save()

    self.log_in_testy()

    response = self.client.get(self.url, follow=True)

    self.assertTemplateUsed(response, self.template)
    self.assertContains(response, form_data['intro'])
    self.assertContains(response, '<textarea', count=1)
    self.assertContains(response, '<li><label for', count=2)

  def pre_create_survey(self):
    # Create survey and connect it to GP 1
    survey = models.Survey(
        title='Basic Survey',
        intro=('Please fill out this quick survey evaluating our last meeting.'
               ' Responses are completely anonymous. Once you have completed '
               'it, you\'ll be taken to your regular home page.'),
        questions = (
          '[{"question": "How well did we meet our goals? (1 = did not meet, 5 = met all our goals)",'
          ' "choices": [1, 2, 3, 4, 5]}, '
          '{"question": "Any other comments for us?", "choices": []}]'))
    survey.save()
    gp_survey = models.GPSurvey(survey=survey, giving_project_id=1, date=timezone.now())
    gp_survey.save()
    self.gps_pk = gp_survey.pk

  def test_fill(self):
    """ Verify that a filled out survey is properly stored

    Setup:
      Log into PC and verify that survey is showing
      Post and check the resulting object
    """
    self.pre_create_survey()
    self.log_in_testy()

    membership = models.Membership.objects.get(pk=1)
    self.assertEqual(membership.completed_surveys, '[]')
    # Make sure survey shows up from home page
    response = self.client.get(self.url, follow=True)
    self.assertTemplateUsed(response, self.template)

    # Verify no responses in DB yet
    self.assertEqual(models.SurveyResponse.objects.count(), 0)

    # Post a survey response
    form_data = {'responses_0': '2',
                 'responses_1': 'No comments.',
                 'date': str(timezone.now()).split('+')[0],
                 'gp_survey': self.gps_pk}
    post_url = reverse('sjfnw.fund.views.gp_survey',
                       kwargs = {'gp_survey': self.gps_pk})
    response = self.client.post(post_url, form_data)

    self.assertEqual(response.content, 'success')
    new_response = models.SurveyResponse.objects.get(gp_survey_id=self.gps_pk)
    self.assertEqual(new_response.responses, json.dumps(
      ["How well did we meet our goals? (1 = did not meet, 5 = met all our goals)", "2",
       "Any other comments for us?", "No comments."]))

  def test_future_survey(self):
    """ Verify that survey doesn't show if the date has not been reached """

    self.pre_create_survey()
    self.log_in_testy()

    # Change survey date to future
    gp_survey = models.GPSurvey.objects.get(giving_project_id=1)
    gp_survey.date = timezone.now() + timedelta(days=20)
    gp_survey.save()

    gp_survey = models.GPSurvey.objects.get(giving_project_id=1)
    # Make sure survey shows up from home page
    response = self.client.get(self.url, follow=True)
    self.assertTemplateNotUsed(response, self.template)

  def test_completed_survey(self):
    """ Verify that survey doesn't show if it has been completed """

    self.pre_create_survey()
    self.log_in_testy()

    # Mark completed
    membership = models.Membership.objects.get(pk=1)
    membership.completed_surveys = '[1]'
    membership.save()

    # Check home page
    response = self.client.get(self.url, follow=True)
    self.assertTemplateNotUsed(self.template)



