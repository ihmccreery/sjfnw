from django.core.urlresolvers import reverse

from sjfnw.fund import models
from sjfnw.fund.tests.base import BaseFundTestCase

class EditContact(BaseFundTestCase):

  def setUp(self):
    super(EditContact, self).setUp()
    self.use_test_acct()
    self.url = reverse('sjfnw.fund.views.edit_contact',
                       kwargs={'donor_id': self.donor_id})
    self.form_data = {
      'phone': '888-888-8888',
      'firstname': 'John',
      'lastname': 'Doe',
      'likelihood': '10',
      'email': 'testacct@gmail.com',
      'notes': 'adifjaoifjdoiajfoa'
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


class DeleteContact(BaseFundTestCase):

  def setUp(self):
    super(DeleteContact, self).setUp()
    self.use_test_acct()
    # set copied contacts to avoid redirect after delete
    membership = models.Membership.objects.get(pk=self.ship_id)
    membership.copied_contacts = True
    membership.save()

  def test_success(self):
    """ Verify success of deleting existing contact """

    donor = models.Donor.objects.get(pk=self.donor_id)
    self.assertEqual(donor.membership_id, self.ship_id)

    url = reverse('sjfnw.fund.views.delete_contact', kwargs={'donor_id': self.donor_id})
    response = self.client.post(url, {}, follow=True)

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'fund/_base_personal.html')
    self.assertTemplateUsed(response, 'fund/forms/add_contacts.html')

    donor = models.Donor.objects.filter(pk=self.donor_id)
    self.assertEqual(len(donor), 0)

  def test_nonexistent(self):
    """ Verify 404 if donor does not exist """

    test_id = 894
    self.assertEqual(0, models.Donor.objects.filter(pk=test_id).count())

    url = reverse('sjfnw.fund.views.delete_contact', kwargs={'donor_id': test_id})
    response = self.client.post(url, {}, follow=True)

    self.assertEqual(response.status_code, 404)

  def test_permission(self):
    """ Verify failure when requesting to delete another membership's contact """

    # switch to newbie account and verify that test donor is not associated with it
    self.use_new_acct()
    test_id = 1
    donor = models.Donor.objects.get(pk=test_id)
    self.assertNotEqual(donor.membership_id, self.pre_id)
    self.assertNotEqual(donor.membership.member_id, self.member_id)

    # visit home page and verify that it loads under the expected membership
    response = self.client.get(reverse('sjfnw.fund.views.home'), follow=True)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.context['request'].membership.pk, self.pre_id)

    # attempt to delete test donor
    url = reverse('sjfnw.fund.views.delete_contact', kwargs={'donor_id': test_id})
    response = self.client.post(url, {}, follow=True)

    self.assertEqual(response.status_code, 404)
