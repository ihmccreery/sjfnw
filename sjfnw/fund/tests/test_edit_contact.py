from django.core.urlresolvers import reverse

from sjfnw.fund import models
from sjfnw.fund.tests.base import BaseFundTestCase

class EditContact(BaseFundTestCase):

  def setUp(self):
    super(EditContact, self).setUp()
    self.use_test_acct()
    self.url = reverse('sjfnw.fund.views.edit_contact',
                       kwargs={'donor_id' : self.donor_id})
    self.form_data = {
      'phone' : '888-888-8888',
      'firstname' : 'John',
      'lastname' : 'Doe',
      'likelihood' : '10',
      'email' : 'testacct@gmail.com',
      'notes' : 'adifjaoifjdoiajfoa'
    }

  def test_negative_amount(self):
    self.form_data['amount'] = '-10'
    response = self.client.post(self.url, self.form_data, follow=True)

    self.assertTemplateUsed(response, 'fund/forms/edit_contact.html')
    self.assertFormError(response, 'form', 'amount', 'Must be greater than or equal to 0.')

  def test_positive_amount(self):
    self.form_data['amount'] = '10'
    response = self.client.post(self.url, self.form_data, follow=True)

    self.assertEqual(response.content, 'success')

    contact = models.Donor.objects.get(pk=self.donor_id)
    self.assertEqual(contact.amount, 10)
