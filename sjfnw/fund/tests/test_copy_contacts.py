import logging

from django.core.urlresolvers import reverse

from sjfnw.fund import models
from sjfnw.fund.tests.base import BaseFundTestCase

logger = logging.getLogger('sjfnw')


class CopyContacts(BaseFundTestCase):
  """ Test copy_contacts view """

  get_url = reverse('sjfnw.fund.views.home')
  post_url = reverse('sjfnw.fund.views.copy_contacts')
  template = 'fund/forms/copy_contacts.html'

  def setUp(self):
    super(CopyContacts, self).setUp()
    self.use_test_acct()

    # create a new empty membership for testy, set as current
    pre = models.GivingProject.objects.get(title='Pre training')
    membership = models.Membership(giving_project=pre, member_id=self.member_id,
                                   approved=True)
    membership.save()
    self.membership = membership
    member = models.Member.objects.get(email='testacct@gmail.com')
    member.current = membership.pk
    member.save()

  def test_no_duplicates(self):
    """ Verify that form display & submits properly without dup contacts

    Setup:
      Use a member that has existing contacts
      Create fresh membership
      Go to home page

    Asserts:
      After post, number of donors associated with membership = number in form
    """

    member = models.Member.objects.get(email='testacct@gmail.com')

    response = self.client.get(self.get_url, follow=True)

    self.assertTemplateUsed(response, self.template)
    formset = response.context['formset']
    self.assertEqual(formset.initial_form_count(),
                     models.Donor.objects.filter(membership__member=member).count())

    self.assertEqual(0, models.Donor.objects.filter(membership=self.membership).count())

    post_data = {'form-MAX_NUM_FORMS': 1000}
    post_data['form-INITIAL_FORMS'] = formset.initial_form_count()
    post_data['form-TOTAL_FORMS'] = formset.initial_form_count()
    index = 0
    for contact in formset.initial:
      post_data['form-%d-email' % index] = contact['email']
      post_data['form-%d-firstname' % index] = contact['firstname']
      post_data['form-%d-lastname' % index] = contact['lastname']
      post_data['form-%d-email' % index] = contact['email']
      post_data['form-%d-notes' % index] = contact['notes']
      post_data['form-%d-select' % index] = 'on'
      index += 1

    response = self.client.post(self.post_url, post_data)

    self.assertEqual(formset.initial_form_count(),
                     models.Donor.objects.filter(membership=self.membership).count())

  def test_merge_duplicates(self):
    """ Verify proper merging of contacts

    Setup:
      Add duplicates in all 3 ways (last, phone, email). Each adds/contradicts
      Get copy contacts view and see how it has handled merge

    Asserts:
      Only 13 initial forms are shown
      For the 3 modified ones, asserts fields have the intended values
    """
    member = models.Member.objects.get(email='testacct@gmail.com')
    unique_donors = models.Donor.objects.filter(membership__member=member).count()

    copy = models.Donor(membership_id=1, firstname="Lyn", lastname="Long",
                        notes="An alliterative fellow.")
    copy.save()
    copy = models.Donor(membership_id=1, firstname="Nate",
                        email="nat@yahoo.com")
    copy.save()
    copy = models.Donor(membership_id=1, firstname="Patice", lastname="Attison",
                        phone="555-555-8956")
    copy.save()

    response = self.client.get(self.get_url, follow=True)

    self.assertTemplateUsed(response, self.template)
    formset = response.context['formset']
    self.assertEqual(formset.initial_form_count(), unique_donors)

    self.assertContains(response, 'An alliterative fellow')
    self.assertContains(response, 'Attison')

  def test_skip(self):
    """ Verify that skip works

    Setup:
      Use a member with past contacts, new membership
      Enter skip in form

    Asserts:
      Response shows home page
      membership.copied_contacts is set to true
      Reload home page - copy not shown
    """

    # show that copy contacts shows up
    self.assertFalse(self.membership.copied_contacts)
    response = self.client.get(self.get_url, follow=True)
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(self.template)

    # post a skip
    response = self.client.post(self.post_url, {'skip': 'True'})

    # show that it was marked on membership and the form is not triggered
    membership = models.Membership.objects.get(pk=self.membership.pk)
    self.assertTrue(membership.copied_contacts)
    response = self.client.get(self.get_url, follow=True)
    self.assertTemplateNotUsed(self.template)
