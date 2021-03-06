import datetime, logging

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.safestring import mark_safe

from sjfnw.fund.models import GivingProject
from sjfnw.grants import constants as gc
from sjfnw.grants.models import (Organization, GrantCycle, GrantApplication,
    DraftGrantApplication)

logger = logging.getLogger('sjfnw')


class LoginForm(forms.Form):
  email = forms.EmailField(max_length=255)
  password = forms.CharField(widget=forms.PasswordInput())


class RegisterForm(forms.Form):
  email = forms.EmailField(max_length=255)
  password = forms.CharField(widget=forms.PasswordInput())
  passwordtwo = forms.CharField(widget=forms.PasswordInput(), label='Re-enter password')
  organization = forms.CharField()

  def clean(self):
    cleaned_data = super(RegisterForm, self).clean()
    org = cleaned_data.get('organization')
    email = cleaned_data.get('email')

    if org and email:
      if Organization.objects.filter(email=email):
        logger.warning(u'%s tried to re-register with %s', org, email)
        raise ValidationError('That email is already registered. Log in instead.')

      name_match = Organization.objects.filter(name__iexact=org)
      if name_match:
        if name_match[0].email:
          logger.warning(u'Name match on registration, different emails: %s', org)
          raise ValidationError('That organization is already registered. Log in instead.')
        else:
          logger.warning('Name match, blank email. ' + org)

      if User.objects.filter(username=email):
        logger.warning(u'User already exists, but not Org: %s', email)
        raise ValidationError('That email is registered with Project Central.'
                              ' Please register using a different email.')

      password = cleaned_data.get('password')
      passwordtwo = cleaned_data.get('passwordtwo')
      if password and passwordtwo and password != passwordtwo:
        raise ValidationError('Passwords did not match.')

    return cleaned_data


class CheckMultiple(forms.widgets.CheckboxSelectMultiple):
  """ Multiple-select checkbox widget with select all/none shortcuts """

  def render(self, name, value, attrs=None, choices=()):
    rendered = super(CheckMultiple, self).render(name, value, attrs, choices)
    shortcuts = ('[<a onclick="check(\'{0}\', true)">all</a>] '
                 '[<a onclick="check(\'{0}\', false)">none</a>]')
    return mark_safe(shortcuts.format(name) + rendered)


class RolloverForm(forms.Form):
  """ Used by organizations to copy a draft or app into another grant cycle

  Fields (created on init):
    application - any of org's submitted apps
    draft - any of org's drafts
    cycle - any open cycle that does not have a submission or draft
  """

  def __init__(self, organization, *args, **kwargs):
    super(RolloverForm, self).__init__(*args, **kwargs)

    submitted = (GrantApplication.objects.select_related('grant_cycle')
                                         .filter(organization=organization)
                                         .order_by('-submission_time'))
    drafts = (DraftGrantApplication.objects.select_related('grant_cycle')
                                           .filter(organization=organization))

    # filter out cycles covered by apps/drafts, get remaining open ones
    exclude_cycles = ([draft.grant_cycle.pk for draft in drafts] +
                      [sub.grant_cycle.pk for sub in submitted])
    cycles = (GrantCycle.objects.filter(open__lt=timezone.now(), close__gt=timezone.now())
                                .exclude(id__in=exclude_cycles))

    # create fields
    self.fields['application'] = forms.ChoiceField(
        required=False, initial=0,
        choices=[('', '--- Submitted applications ---')] +
                [(a.id, u'{} - submitted {:%m/%d/%y}'.format(a.grant_cycle, a.submission_time))
                 for a in submitted])
    self.fields['draft'] = forms.ChoiceField(
        required=False, initial=0,
        choices=[('', '--- Saved drafts ---')] +
                [(d.id, u'{} - modified {:%m/%d/%y}'.format(d.grant_cycle, d.modified))
                 for d in drafts])
    self.fields['cycle'] = forms.ChoiceField(
        choices=[('', '--- Open cycles ---')] + [(c.id, unicode(c)) for c in cycles])

  def clean(self):
    cleaned_data = super(RolloverForm, self).clean()
    cycle = cleaned_data.get('cycle')
    application = cleaned_data.get('application')
    draft = cleaned_data.get('draft')

    if not cycle:
      self._errors['cycle'] = self.error_class(['Required.'])
    else:
      try:
        cycle_obj = GrantCycle.objects.get(pk=int(cycle))
      except GrantCycle.DoesNotExist:
        logger.error('RolloverForm submitted cycle does not exist')
        self._errors['cycle'] = self.error_class(
            ['Grant cycle could not be found. Please refresh the page and try again.'])

      if not cycle_obj.is_open:
        self._errors['cycle'] = self.error_class(
            ['That cycle has closed.  Select a different one.'])

    if not draft and not application:
      self._errors['draft'] = self.error_class(['Select one.'])
    elif draft and application:
      self._errors['draft'] = self.error_class(['Select only one.'])

    return cleaned_data


class AdminRolloverForm(forms.Form):
  def __init__(self, organization, *args, **kwargs):
    super(AdminRolloverForm, self).__init__(*args, **kwargs)

    submitted = (GrantApplication.objects.select_related('grant_cycle')
                                         .filter(organization=organization)
                                         .order_by('-submission_time'))
    drafts = (DraftGrantApplication.objects.select_related('grant_cycle')
                                           .filter(organization=organization))

    # get last 6 mos of cycles
    cutoff = timezone.now() - datetime.timedelta(days=180)
    exclude_cycles = [d.grant_cycle.pk for d in drafts] + [a.grant_cycle.pk for a in submitted]
    cycles = GrantCycle.objects.filter(close__gt=cutoff).exclude(id__in=exclude_cycles)

    # create field
    self.fields['cycle'] = forms.ChoiceField(
        choices=[('', '--- Grant cycles ---')] + [(c.id, unicode(c)) for c in cycles])


class RolloverYERForm(forms.Form):
  """ Used to copy a year-end report for use with another gp grant
  Fields (created on init):
    report - submitted YearEndReport
    award - GPGrant to copy it to
  """

  def __init__(self, reports, awards, *args, **kwargs):
    super(RolloverYERForm, self).__init__(*args, **kwargs)
    self.fields['report'] = forms.ChoiceField(
        choices=[('', '--- Year-end reports ---')] +
                [(r.id, unicode(r) + ' ({:%-m/%-d/%y})'.format(r.submitted)) for r in reports])
    self.fields['award'] = forms.ChoiceField(
        label='Grant', choices=[('', '--- Grants ---')] + [(a.id, unicode(a)) for a in awards])


class BaseReportForm(forms.Form):
  """ Abstract form for fields shared between all report types """

  # filters
  organization_name = forms.CharField(max_length=255, required=False,
      help_text='Organization name must contain the given text')
  city = forms.CharField(max_length=255, required=False,
      help_text='City must match the given text')
  state = forms.MultipleChoiceField(choices=gc.STATE_CHOICES[:5],
      widget=forms.CheckboxSelectMultiple, required=False)
  has_fiscal_sponsor = forms.BooleanField(required=False)

  # fields
  report_contact = forms.MultipleChoiceField(
      label='Contact', required=False,
      widget=CheckMultiple, choices=[
        ('contact_person', 'Contact person name'),
        ('contact_person_title', 'Contact person title'),
        ('address', 'Address'),
        ('city', 'City'),
        ('state', 'State'),
        ('zip', 'ZIP'),
        ('telephone_number', 'Telephone number'),
        ('fax_number', 'Fax number'),
        ('email_address', 'Email address'),
        ('website', 'Website')
      ])
  report_org = forms.MultipleChoiceField(
      label='Organization', required=False,
      widget=CheckMultiple, choices=[
        ('status', 'Status'),
        ('ein', 'EIN'),
        ('founded', 'Year founded')
      ])
  report_fiscal = forms.BooleanField(label='Fiscal sponsor', required=False)

  format = forms.ChoiceField(choices=[('csv', 'CSV'), ('browse', 'Don\'t export, just browse')])

  class Meta:
    abstract = True


class BaseAppRelatedReportForm(BaseReportForm):

  year_min = forms.ChoiceField(
      choices=[(n, n) for n in range(timezone.now().year, 1990, -1)],
      initial=timezone.now().year - 1)
  year_max = forms.ChoiceField(
      choices=[(n, n) for n in range(timezone.now().year, 1990, -1)])
  giving_projects = forms.MultipleChoiceField(
      choices=[], widget=forms.CheckboxSelectMultiple, required=False)
  grant_cycle = forms.MultipleChoiceField(required=False, choices=[],
      widget=forms.CheckboxSelectMultiple)

  def __init__(self, *args, **kwargs):
    super(BaseAppRelatedReportForm, self).__init__(*args, **kwargs)

    choices = GivingProject.objects.values_list('title', flat=True).distinct().order_by('title')
    choices = [(g, g) for g in choices]
    self.fields['giving_projects'].choices = choices

    choices = GrantCycle.objects.values_list('title', flat=True).distinct().order_by('title')
    choices = [(g, g) for g in choices]
    self.fields['grant_cycle'].choices = choices

  def clean(self):
    cleaned_data = super(BaseAppRelatedReportForm, self).clean()
    if cleaned_data['year_max'] < cleaned_data['year_min']:
      raise ValidationError('Start year must be less than or equal to end year.')
    return cleaned_data


class AppReportForm(BaseAppRelatedReportForm):

  pre_screening_status = forms.MultipleChoiceField(
      choices=gc.PRE_SCREENING,
      widget=forms.CheckboxSelectMultiple, required=False)
  screening_status = forms.MultipleChoiceField(label='Giving project screening status',
      choices=gc.SCREENING,
      widget=forms.CheckboxSelectMultiple, required=False)
  poc_bonus = forms.BooleanField(required=False)
  geo_bonus = forms.BooleanField(required=False)

  report_basics = forms.MultipleChoiceField(
      label='Basics', required=False,
      widget=CheckMultiple, choices=[
        ('id', 'Unique id number'),
        ('pre_screening_status', 'Pre-screening status')
      ])
  report_proposal = forms.MultipleChoiceField(
      label='Grant request and project', required=False,
      widget=CheckMultiple, choices=[
        ('amount_requested', 'Amount requested'),
        ('grant_request', 'Description of grant request'),
        ('support_type', 'Support type'),
        ('grant_period', 'Grant period'),
        ('project_title', 'Project title'),
        ('project_budget', 'Project budget'),
        ('previous_grants', 'Previous grants from SJF')
      ])
  report_budget = forms.MultipleChoiceField(
      label='Budget', required=False,
      widget=CheckMultiple, choices=[
        ('start_year', 'Start of fiscal year'),
        ('budget_last', 'Budget last year'),
        ('budget_current', 'Budget current year')
      ])
  report_collab = forms.BooleanField(label='Collaboration references',
      required=False)
  report_racial_ref = forms.BooleanField(label='Racial justice references',
      required=False)
  report_bonuses = forms.BooleanField(label='Scoring bonuses', required=False)
  report_gps = forms.BooleanField(label='Assigned giving_project(s)', required=False)
  report_gp_screening = forms.BooleanField(label='GP screening status', required=False)
  report_award = forms.BooleanField(label='Grant awards', required=False)


class GPGrantReportForm(BaseAppRelatedReportForm):

  report_id = forms.BooleanField(required=False, label='Unique ID number')
  report_check_number = forms.BooleanField(required=False, label='Check number')
  report_date_approved = forms.BooleanField(required=False, label='Date approved by E.D.')
  report_support_type = forms.BooleanField(required=False, label='Support type')
  report_agreement_dates = forms.BooleanField(required=False,
      label='Date agreement mailed/returned')
  report_year_end_report_due = forms.BooleanField(required=False,
      label='Date year end report due')


class SponsoredAwardReportForm(BaseReportForm):

  year_min = forms.ChoiceField(
      choices=[(n, n) for n in range(timezone.now().year, 1990, -1)],
      initial=timezone.now().year - 1)
  year_max = forms.ChoiceField(
      choices=[(n, n) for n in range(timezone.now().year, 1990, -1)])
  report_id = forms.BooleanField(required=False, label='ID number')
  report_check_number = forms.BooleanField(required=False, label='Check number')
  report_date_approved = forms.BooleanField(required=False, label='Date approved by E.D.')

  def clean(self):
    cleaned_data = super(SponsoredAwardReportForm, self).clean()
    if cleaned_data['year_max'] < cleaned_data['year_min']:
      raise ValidationError('Start year must be less than or equal to end year.')
    return cleaned_data


class OrgReportForm(BaseReportForm):

  # filters
  registered = forms.ChoiceField(choices=[('None', '---'), ('True', 'yes'), ('False', 'no')])

  # fields
  report_account_email = forms.BooleanField(label='Login email', required=False)
  report_applications = forms.BooleanField(label='List of applications', required=False)
  report_awards = forms.BooleanField(label='List of awards', required=False)


class LoginAsOrgForm(forms.Form):

  def __init__(self, *args, **kwargs):
    super(LoginAsOrgForm, self).__init__(*args, **kwargs)
    orgs = Organization.objects.order_by('name')
    self.fields['organization'] = forms.ChoiceField(
        choices=[('', '--- Organizations ---')] + [(o.email, unicode(o)) for o in orgs])


class OrgMergeForm(forms.Form):

  primary = forms.ChoiceField(widget=forms.widgets.RadioSelect,
                              error_messages={'required': 'Please select one'})

  def __init__(self, org_a, org_b, *args, **kwargs):
    super(OrgMergeForm, self).__init__(*args, **kwargs)

    self.fields['primary'].choices = [(org_a.pk, ''), (org_b.pk, '')]
