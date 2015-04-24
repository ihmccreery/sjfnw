import logging

from django.core.urlresolvers import reverse
from django.utils import timezone

from sjfnw.fund import models
from sjfnw.fund.views import _compile_membership_progress
from sjfnw.fund.tests.base import BaseFundTestCase

logger = logging.getLogger('sjfnw')

class AddContacts(BaseFundTestCase):

  url = reverse('sjfnw.fund.views.home')

  def setUp(self):
    super(AddContacts, self).setUp()
    self.use_new_acct()

  def test_new(self):
    """ Verify that add mult form is shown to new memberships """

    # using pre-training membership

    membership = models.Membership.objects.get(pk=self.pre_id)

    response = self.client.get(self.url, follow=True)

    self.assertTemplateUsed(response, 'fund/forms/add_contacts.html')
    self.assertEqual(response.context['request'].membership, membership)
    self.assertNotContains(response, 'likelihood')

    # using post-training membership

    member = models.Member.objects.get(pk=self.member_id)
    member.current = self.post_id
    member.save()
    membership = models.Membership.objects.get(pk=self.post_id)

    response = self.client.get(self.url, follow=True)

    self.assertTemplateUsed(response, 'fund/forms/add_contacts.html')
    self.assertEqual(response.context['request'].membership, membership)
    self.assertContains(response, 'likelihood')

  def test_contacts_without_est(self):
    """ Going to home page with contacts that do not have estimates """

    # using pre-training membership
    membership = models.Membership.objects.get(pk=self.pre_id)

    # create contacts without amount or likelihood
    contact1 = models.Donor(firstname='Anna', membership=membership)
    contact1.save()
    contact2 = models.Donor(firstname='Banana', membership=membership)
    contact2.save()

    response = self.client.get(self.url)

    # verify estimates form is not shown
    self.assertEqual(response.context['request'].membership, membership)
    self.assertTemplateNotUsed('fund/forms/add_estimates.html')

    # using post-training membership
    member = membership.member
    member.current = self.post_id
    member.save()

    membership = models.Membership.objects.get(pk=self.post_id)

    # move created contacts to current membership
    contact1.membership = membership
    contact1.save()
    contact2.membership = membership
    contact2.save()

    response = self.client.get(self.url, follow=True)

    # verify estimates form is shown
    self.assertTemplateUsed('fund/forms/add_estimates.html')
    self.assertEqual(response.context['request'].membership, membership)

class AddEstimates(BaseFundTestCase):

  url = reverse('sjfnw.fund.views.home')

  def setUp(self):
    super(AddEstimates, self).setUp()
    self.use_new_acct()

  def test_estimates_done(self):
    """ Verify add estimates form is not shown if contacts have estimates """

    # use post-training membership
    membership = models.Membership.objects.get(pk=self.post_id)
    member = membership.member
    member.current = self.post_id
    member.save()

    # create contacts with amount & likelihood
    contact = models.Donor(firstname='Anna', membership=membership, amount=0, likelihood=0)
    contact.save()
    contact = models.Donor(firstname='Banana', membership=membership, amount=567, likelihood=34)
    contact.save()

    response = self.client.get(self.url)

    # verify estimates form is not shown
    self.assertTemplateNotUsed('fund/forms/add_estimates.html')
    self.assertEqual(response.context['request'].membership, membership)


class HomeSurveys(BaseFundTestCase):

  url = reverse('sjfnw.fund.views.home')

  def setUp(self):
    super(HomeSurveys, self).setUp()
    self.use_test_acct()
    survey = models.Survey(title='First Meeting')
    survey.save()
    self.survey_id = survey.pk
    gp = models.GivingProject.objects.get(title='Post training')
    gpsurvey = models.GPSurvey(survey_id=survey.pk, giving_project=gp,
                               date=timezone.now())
    gpsurvey.save()

  def test_survey_shown(self):
    membership = models.Membership.objects.get(pk=self.ship_id)
    self.assertEqual(membership.completed_surveys, '[]')

    response = self.client.get(self.url, follow=True)

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'fund/forms/gp_survey.html')

  def test_surveys_complete(self):
    membership = models.Membership.objects.get(pk=self.ship_id)
    membership.completed_surveys = '[{}]'.format(self.survey_id)
    membership.save()

    response = self.client.get(self.url, follow=True)

    self.assertEqual(response.status_code, 200)
    self.assertTemplateNotUsed(response, 'fund/forms/gp_survey.html')


class CompileMembershipProgress(BaseFundTestCase):
  """ Test _compile_membership_progress method used by home view """

  def setUp(self):
    super(CompileMembershipProgress, self).setUp()

  def test_empty(self):
    donor_data, progress = _compile_membership_progress([])

    self.assertEqual(donor_data, {})
    for _, value in progress.iteritems():
      self.assertEqual(value, 0)

  def test_single(self):
    # membership with a few donors, some progress
    self.use_test_acct()
    donors = models.Donor.objects.filter(membership_id=self.ship_id)

    donor_data, progress = _compile_membership_progress(donors)

    for donor in donors:
      data = donor_data[donor.pk]
      self.assertIsInstance(data, dict)
    self.assertIsInstance(progress, dict)
    self.assertEqual(progress['contacts'], len(donors))
