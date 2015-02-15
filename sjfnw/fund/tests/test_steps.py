import logging
import unittest

from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from sjfnw.fund import models
from sjfnw.fund.tests.base import BaseFundTestCase, TEST_FIXTURE

logger = logging.getLogger('sjfnw')


class StepComplete(BaseFundTestCase):
  """ Tests various scenarios of step completion
  1) completion
    a) minimal step complete - verify step & donor updated
    b) when different stages have already been reached (asked, responded, promised)
       verify display and submission handling
    c) for each additional step, try minimal (no additional data), contradictory/invalid if
       applicable, and full valid
  2) contact notes
  3) next step
    a) validation
    b) creation """

  fixtures = TEST_FIXTURE

  def setUp(self):
    logger.info('BaseFundTestCase setUp')
    super(StepComplete, self).setUp()
    logger.info('post super')
    self.use_test_acct()
    self.url = reverse('sjfnw.fund.views.done_step', kwargs={
        'donor_id': self.donor_id, 'step_id': self.step_id
      })
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
        'likely_to_join': ''}

    # 'asked': 'on', 'promise_reason': ['GP topic', 'Social justice']

  # helper function used by >1 test
  def add_followup(self):

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
    self.assertEqual(response.content, "success")

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
    self.assertEqual(response.content, "success")

    step = models.Step.objects.get(pk=self.step_id)
    donor = models.Donor.objects.get(pk=self.donor_id)

    self.assertIsNotNone(step.completed)
    self.assertTrue(step.asked)
    self.assertTrue(donor.asked)

  def test_minimal_next(self):
    """ Verify success of blank form with a next step

    Setup:
      Only form info is next step and next step date

    Asserts:
      Success response
      Step completed
      New step added to DB
    """

    form_data = {'asked': '',
        'response': 2,
        'promised_amount': '',
        'last_name': '',
        'notes': '',
        'next_step': 'A BRAND NEW STEP',
        'next_step_date': '2013-01-25'}

    pre_count = models.Step.objects.count()

    response = self.client.post(self.url, form_data)
    self.assertEqual(response.content, "success")

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

  def valid_followup(self, form_data):
    """ Not a test in itself - used by valid follow up tests

    Asserts:
      Success response
      if response is 1 (promised)
        Donor last name and/or email match form input
        Step & donor promised=form amount
      if response is 3 (declined)
        donor and step promised = 0
      if response is 2 or 3
        last name, email, promised amount are not updated
      Donor asked=True
      Step completed
      Step asked=True
    """

    pre_donor = models.Donor.objects.get(pk=self.donor_id)

    response = self.client.post(self.url, form_data)
    self.assertEqual(response.content, "success")

    promised = form_data['promised_amount']
    if promised == '5,000': #hacky workaround
      promised = 5000

    # step completion, asked update
    donor1 = models.Donor.objects.get(pk=self.donor_id)
    step1 = models.Step.objects.get(pk=self.step_id)
    self.assertTrue(donor1.asked)
    self.assertTrue(step1.asked)
    self.assertIsNotNone(step1.completed)

    # follow up info
    if form_data['response'] == 1:
      self.assertEqual(donor1.lastname, form_data['last_name'])
      self.assertEqual(donor1.email, form_data['email'])
      self.assertEqual(donor1.phone, form_data['phone'])
      self.assertEqual(donor1.promised, promised)
      self.assertEqual(step1.promised, promised)
    else:
      if form_data['response'] == 3: #declined
        self.assertEqual(donor1.promised, 0)
        self.assertEqual(step1.promised, 0)
      else:
        self.assertEqual(donor1.promised, pre_donor.promised)
        self.assertIsNone(step1.promised)
      self.assertEqual(donor1.lastname, pre_donor.lastname)
      self.assertEqual(donor1.phone, pre_donor.phone)
      self.assertEqual(donor1.email, pre_donor.email)


  def test_valid_followup(self):
    """ Verify success of promise with amount, last name and email

    Setup:
      Form contains asked, response = promised, amount = 50,
        includes last name and email

    Asserts:
      See valid_followup
    """

    self.form_data['asked'] = 'on'
    self.form_data['response'] = 1
    self.form_data['promised_amount'] = 50
    self.add_followup()

    self.valid_followup(self.form_data)

  def test_valid_followup_comma(self):
    """ Verify success of promise when amount has comma in it
        (Test whether IntegerCommaField works)

    Setup:
      Form = followup2 except amount = '5,000'

    Asserts:
      See valid_followup
    """

    self.form_data['asked'] = 'on'
    self.form_data['response'] = 1
    self.form_data['promised_amount'] = '5,000'
    self.add_followup()

    self.valid_followup(self.form_data)

  def test_valid_hiddendata1(self):

    """ promise amt + follow up + undecided
      amt & follow up info should not be saved """

    self.form_data['asked'] = 'on'
    self.form_data['response'] = 2
    self.form_data['promised_amount'] = 50
    self.form_data['last_name'] = 'Sozzity'
    self.form_data['phone'] = '206-555-5898'

    self.valid_followup(self.form_data)

  def test_valid_hiddendata2(self):

    """ declined + promise amt + follow up
      amt & follow up info should not be saved
      step.promised & donor.promised = 0 """

    form_data = {'asked': 'on',
      'response': 3,
      'promised_amount': 50,
      'last_name': 'Sozzity',
      'phone': '206-555-5898',
      'email': '',
      'notes': '',
      'next_step': '',
      'next_step_date': ''}

    self.valid_followup(form_data)

  def test_valid_hiddendata3(self):

    """ promise amt + follow up + undecided
      allow without followup
      don't save promise on donor or step """

    form_data = {'asked': 'on',
      'response': 2,
      'promised_amount': 50,
      'last_name': '',
      'phone': '',
      'email': '',
      'notes': '',
      'next_step': '',
      'next_step_date': ''}

    self.valid_followup(form_data)

  def test_invalid_promise(self):
    """ Verify that additional info is required when a promise is entered

    Setup:
      Complete a step with response promised, but no amount, phone or email

    Asserts:
      Form template used (not successful)
      Form errors on promised_amount, last_name, phone
      Step and donor not modified
    """

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

    self.assertTemplateUsed(response, 'fund/done_step.html')
    self.assertFormError(response, 'form', 'promised_amount', "Enter an amount.")
    self.assertFormError(response, 'form', 'last_name', "Enter a last name.")
    self.assertFormError(response, 'form', 'phone', "Enter a phone number or email.")

    step1 = models.Step.objects.get(pk=self.step_id)
    donor1 = models.Donor.objects.get(pk=self.donor_id)

    self.assertIsNone(step1.completed)
    self.assertFalse(step1.asked)
    self.assertFalse(donor1.asked)

  def test_invalid_next(self):

    """ missing date
        missing desc """

    form_data = {'asked': '',
        'response': 2,
        'promised_amount': '',
        'last_name': '',
        'notes': '',
        'next_step': 'A step description!',
        'next_step_date': ''}

    response = self.client.post(self.url, form_data)

    self.assertTemplateUsed(response, 'fund/done_step.html')
    self.assertFormError(response, 'form', 'next_step_date', "Enter a date in mm/dd/yyyy format.")

    step1 = models.Step.objects.get(pk=self.step_id)
    self.assertIsNone(step1.completed)

    form_data = {'asked': '',
        'response': 2,
        'promised_amount': '',
        'last_name': '',
        'notes': '',
        'next_step': '',
        'next_step_date': '2013-01-25'}

    response = self.client.post(self.url, form_data)
    self.assertTemplateUsed(response, 'fund/done_step.html')
    self.assertFormError(response, 'form', 'next_step', "Enter a description.")

    step1 = models.Step.objects.get(pk=self.step_id)
    self.assertIsNone(step1.completed)

