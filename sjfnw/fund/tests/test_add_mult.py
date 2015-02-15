from django.core.urlresolvers import reverse

from sjfnw.fund import models
from sjfnw.fund.tests.base import BaseFundTestCase, TEST_FIXTURE

class AddMultipleDonorsPre(BaseFundTestCase):
  
  fixtures = TEST_FIXTURE
  url = reverse('sjfnw.fund.views.add_mult')

  def setUp(self):
    super(AddMultipleDonorsPre, self).setUp()
    self.use_new_acct()
    self.base_form_data = {
      'form-TOTAL_FORMS': u'5',
      'form-INITIAL_FORMS': u'0',
      'form-MAX_NUM_FORMS': u'1000'
    }
    for i in range(0, 5):
      self.base_form_data['form-%d-firstname' % i] = u''
      self.base_form_data['form-%d-lastname' % i] = u''

  def test_get(self):
    response = self.client.get(self.url, follow=True)

    self.assertTemplateUsed(response, 'fund/add_mult_flex.html')

  def test_post_empty(self):
    response = self.client.post(self.url, self.base_form_data, follow=True)

    self.assertTemplateUsed(response, 'fund/add_mult_flex.html')
    error = response.context['empty_error']
    self.assertRegexpMatches(error, 'enter at least one contact')

  def test_post_first_name(self):
    self.base_form_data['form-0-firstname'] = 'First'

    response = self.client.post(self.url, self.base_form_data, follow=True)

    self.assertEqual(response.content, 'success')

    donor = models.Donor.objects.get(membership_id=self.pre_id, firstname='First')

  def test_post_multiple_valid(self):
    self.base_form_data['form-0-firstname'] = 'First'
    self.base_form_data['form-1-firstname'] = 'Seattle'
    self.base_form_data['form-1-lastname'] = 'Washington'

    response = self.client.post(self.url, self.base_form_data, follow=True)

    self.assertEqual(response.content, 'success')

    donor = models.Donor.objects.get(membership_id=self.pre_id, firstname='First')
    donor = models.Donor.objects.get(membership_id=self.pre_id, firstname='Seattle', lastname='Washington')

  def test_post_multiple_invalid(self):
    self.base_form_data['form-0-lastname'] = 'Last'
    self.base_form_data['form-1-firstname'] = 'Seattle'
    self.base_form_data['form-1-lastname'] = 'Washington'
    self.base_form_data['form-3-lastname'] = 'Smith'

    response = self.client.post(self.url, self.base_form_data, follow=True)

    self.assertTemplateUsed(response, 'fund/add_mult_flex.html')

    errors = response.context['formset'].errors
    self.assertRegexpMatches(errors[0]['firstname'][0], 'required')
    self.assertEqual(errors[1], {})
    self.assertEqual(errors[2], {})
    self.assertRegexpMatches(errors[3]['firstname'][0], 'required')

