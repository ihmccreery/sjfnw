import logging
import unittest

from django.core.urlresolvers import reverse

from sjfnw.fund import models
from sjfnw.fund.tests.base import BaseFundTestCase

logger = logging.getLogger('sjfnw')

class AddStep(BaseFundTestCase):

  def setUp(self):
    super(AddStep, self).setUp()
    self.use_new_acct()
    donor = models.Donor(firstname='user', lastname='', membership_id=self.pre_id)
    donor.save()
    self.url = reverse('sjfnw.fund.views.add_step', kwargs={'donor_id': donor.pk})

  def test_blank(self):
    form_data = {
      'date': u'',
      'description': u''
    }
    response = self.client.post(self.url, form_data, follow=True)
    self.assertTemplateUsed(response, 'fund/forms/add_step.html')


class StepComplete(BaseFundTestCase):
  """ Tests various scenarios of step completion """

  def setUp(self):
    super(StepComplete, self).setUp()
    self.use_test_acct()
    self.url = reverse('sjfnw.fund.views.complete_step', kwargs={
      'donor_id': self.donor_id, 'step_id': self.step_id
    })
    # start with blank/defaults form
    self.form_data = {
      'asked': 'on',
      'response': 2,
      'promised_amount': '',
      'last_name': '',
      'email': '',
      'phone': '',
      'notes': '',
      'next_step': '',
      'next_step_date': '',
      'likely_to_join': '',
      'match_expected': '',
      'match_company': ''
    }

  def add_followup(self):
    """ Add valid promise followup data to self.form_data (helper, not a test) """

    self.form_data['last_name'] = 'Sozzity'
    self.form_data['email'] = 'blah@gmail.com'
    self.form_data['promise_reason'] = ['Social justice']
    self.form_data['likely_to_join'] = 1

  def test_minimal_completion(self):
    """ Verify that step can be completed without any additional input """

    # make sure step is not already completed and ask has not been recorded
    step = models.Step.objects.get(pk=self.step_id)
    self.assertIsNone(step.completed)

    response = self.client.post(self.url, self.form_data)
    self.assertEqual(response.content, 'success')

    step = models.Step.objects.get(pk=self.step_id)
    self.assertIsNotNone(step.completed)

  def test_minimal_asked(self):
    """ Verify that an ask can be entered without any other info """

    donor = models.Donor.objects.get(pk=self.donor_id)
    step = models.Step.objects.get(pk=self.step_id)

    # make sure step is not already completed and ask has not been recorded
    self.assertIsNone(step.completed)
    self.assertFalse(step.asked)
    self.assertFalse(donor.asked)

    self.form_data['asked'] = 'on'

    response = self.client.post(self.url, self.form_data)
    self.assertEqual(response.content, 'success')

    step = models.Step.objects.get(pk=self.step_id)
    donor = models.Donor.objects.get(pk=self.donor_id)

    self.assertIsNotNone(step.completed)
    self.assertTrue(step.asked)
    self.assertTrue(donor.asked)

  def test_minimal_next(self):
    """ Verify success of blank form with a next step """

    form_data = {
        'asked': '',
        'response': 2,
        'promised_amount': '',
        'last_name': '',
        'notes': '',
        'next_step': 'A BRAND NEW STEP',
        'next_step_date': '2013-01-25'
    }

    pre_count = models.Step.objects.count()

    response = self.client.post(self.url, form_data)
    self.assertEqual(response.content, 'success')

    old_step = models.Step.objects.get(pk=self.step_id)
    self.assertIsNotNone(old_step.completed)
    self.assertEqual(pre_count + 1, models.Step.objects.count())
    self.assertEqual(1, models.Step.objects.filter(description='A BRAND NEW STEP').count())

  @unittest.skip('Incomplete')
  def test_valid_response(self): #TODO
    """ TO DO
    contact that was already asked
    add a response
    make sure step.asked stays false """
    pass

  def post_and_verify_followup_saved(self, form_data):
    """ Posts the form and verifies success without follow up info saved appropriately

      Not a test in itself - used by valid follow up tests
    """

    pre_donor = models.Donor.objects.get(pk=self.donor_id)

    response = self.client.post(self.url, form_data)
    self.assertEqual(response.content, 'success')

    promised = form_data['promised_amount']
    if promised == '5,000': #hacky workaround
      promised = 5000

    # get donor and step after the POST
    donor = models.Donor.objects.get(pk=self.donor_id)
    step = models.Step.objects.get(pk=self.step_id)

    # step completion, asked update
    self.assertTrue(donor.asked)
    self.assertTrue(step.asked)
    self.assertIsNotNone(step.completed)

    # follow up info
    if form_data['response'] == 1:
      self.assertEqual(donor.lastname, form_data['last_name'])
      self.assertEqual(donor.email, form_data['email'])
      self.assertEqual(donor.phone, form_data['phone'])
      self.assertEqual(donor.promised, promised)
      self.assertEqual(step.promised, promised)
      if form_data['match_expected'] or form_data['match_company']:
        self.assertEqual(donor.match_expected, form_data['match_expected'])
        self.assertEqual(donor.match_company, form_data['match_company'])
      else:
        self.assertEqual(donor.match_expected, 0)
        self.assertEqual(donor.match_company, '')
    else:
      if form_data['response'] == 3: # declined
        self.assertEqual(donor.promised, 0)
        self.assertEqual(step.promised, 0)
      else:
        self.assertEqual(donor.promised, pre_donor.promised)
        self.assertIsNone(step.promised)
      self.assertEqual(donor.lastname, pre_donor.lastname)
      self.assertEqual(donor.phone, pre_donor.phone)
      self.assertEqual(donor.email, pre_donor.email)


  def test_valid_followup(self):
    """ Success with promise amount, last name and email """

    self.form_data['asked'] = 'on'
    self.form_data['response'] = 1
    self.form_data['promised_amount'] = 50
    self.add_followup()

    self.post_and_verify_followup_saved(self.form_data)

  def test_valid_followup_comma(self):
    """ Success when promise amount has comma in it

      Test whether IntegerCommaField works
      Same as test_valid_followup except except amount = '5,000'
    """

    self.form_data['asked'] = 'on'
    self.form_data['response'] = 1
    self.form_data['promised_amount'] = '5,000'
    self.add_followup()

    self.post_and_verify_followup_saved(self.form_data)

  def test_valid_hiddendata1(self):
    """ Promise data not saved if response is undecided """

    self.form_data['asked'] = 'on'
    self.form_data['response'] = 2
    self.form_data['promised_amount'] = 50
    self.form_data['last_name'] = 'Sozzity'
    self.form_data['phone'] = '206-555-5898'

    self.post_and_verify_followup_saved(self.form_data)

  def test_valid_hiddendata2(self):
    """ Promise followup not saved if response is declined

      step.promised and donor.promised are set to 0
    """

    form_data = {
      'asked': 'on',
      'response': 3,
      'promised_amount': 50,
      'last_name': 'Sozzity',
      'phone': '206-555-5898',
      'email': '',
      'notes': '',
      'next_step': '',
      'next_step_date': ''
    }

    self.post_and_verify_followup_saved(form_data)

  def test_valid_hiddendata3(self):
    """ Followup not required if promise amount is entered but response is undecided """

    form_data = {'asked': 'on',
      'response': 2,
      'promised_amount': 50,
      'last_name': '',
      'phone': '',
      'email': '',
      'notes': '',
      'next_step': '',
      'next_step_date': ''}

    self.post_and_verify_followup_saved(form_data)

  def test_invalid_promise(self):
    """ Additional info is required when a promise is entered """

    form_data = {
        'asked': 'on',
        'response': 1,
        'promised_amount': '',
        'last_name': '',
        'notes': '',
        'next_step': '',
        'next_step_date': ''}

    step1 = models.Step.objects.get(pk=self.step_id)
    donor1 = models.Donor.objects.get(pk=self.donor_id)

    self.assertIsNone(step1.completed)
    self.assertFalse(step1.asked)
    self.assertFalse(donor1.asked)

    response = self.client.post(self.url, form_data)

    self.assertTemplateUsed(response, 'fund/forms/complete_step.html')
    self.assertFormError(response, 'form', 'promised_amount', 'Enter an amount.')
    self.assertFormError(response, 'form', 'last_name', 'Enter a last name.')
    self.assertFormError(response, 'form', 'phone', 'Enter a phone number or email.')

    step1 = models.Step.objects.get(pk=self.step_id)
    donor1 = models.Donor.objects.get(pk=self.donor_id)

    self.assertIsNone(step1.completed)
    self.assertFalse(step1.asked)
    self.assertFalse(donor1.asked)

  def test_invalid_next(self):
    """ Form is not saved, errors are shown if next step is missing date or desc """

    form_data = {'asked': '',
        'response': 2,
        'promised_amount': '',
        'last_name': '',
        'notes': '',
        'next_step': 'A step description!',
        'next_step_date': ''}

    response = self.client.post(self.url, form_data)

    self.assertTemplateUsed(response, 'fund/forms/complete_step.html')
    self.assertFormError(response, 'form', 'next_step_date', 'Enter a date in mm/dd/yyyy format.')

    step1 = models.Step.objects.get(pk=self.step_id)
    self.assertIsNone(step1.completed)

    form_data = {
      'asked': '',
      'response': 2,
      'promised_amount': '',
      'last_name': '',
      'notes': '',
      'next_step': '',
      'next_step_date': '2013-01-25'
    }

    response = self.client.post(self.url, form_data)
    self.assertTemplateUsed(response, 'fund/forms/complete_step.html')
    self.assertFormError(response, 'form', 'next_step', 'Enter a description.')

    step1 = models.Step.objects.get(pk=self.step_id)
    self.assertIsNone(step1.completed)

  def test_match_entered(self):
    """ Match company is required if expected is given """

    self.form_data['asked'] = 'on'
    self.form_data['response'] = 1
    self.form_data['promised_amount'] = 50
    self.add_followup()
    self.form_data['match_expected'] = 100

    response = self.client.post(self.url, self.form_data, follow=True)

    self.assertTemplateUsed(response, 'fund/forms/complete_step.html')
    self.assertFormError(response, 'form', 'match_company', 'Enter the employer\'s name.')

  def test_match_company(self):
    """ Match expected is required if company is given """

    self.form_data['asked'] = 'on'
    self.form_data['response'] = 1
    self.form_data['promised_amount'] = 50
    self.add_followup()
    self.form_data['match_company'] = 'Company X'

    response = self.client.post(self.url, self.form_data, follow=True)

    self.assertTemplateUsed(response, 'fund/forms/complete_step.html')
    self.assertFormError(response, 'form', 'match_expected', 'Enter the amount matched.')

  def test_both_match_fields(self):
    """ Success and match info saved if both fields are entered """

    self.form_data['asked'] = 'on'
    self.form_data['response'] = 1
    self.form_data['promised_amount'] = 50
    self.add_followup()
    self.form_data['match_expected'] = 100
    self.form_data['match_company'] = 'Company X'

    self.post_and_verify_followup_saved(self.form_data)

