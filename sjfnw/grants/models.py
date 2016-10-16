from datetime import timedelta
import json, logging, string

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.db import models
from django.utils import timezone

from sjfnw.fund.models import GivingProject
from sjfnw.grants import constants as gc

logger = logging.getLogger('sjfnw')


class OrganizationManager(models.Manager):

  def create_with_user(self, email=None, password=None, name=None):

    if self.filter(user__username=email):
      raise ValueError('That email is already registered.')

    name_match = self.filter(name=name, user__isnull=True).first()
    if name_match:
      # Organization without User - register but flag inactive
      name_match.user = User.objects.create_user(
          email, email, password, first_name=name[:29], last_name='(Organization)'
      )
      name_match.user.is_active = False
      name_match.user.save()
      name_match.save()
      return name_match

    user = User.objects.create_user(email, email, password,
                                    first_name=name[:29], last_name='(Organization)')
    # TODO remove email
    org = self.model(user=user, name=name, email=email)
    org.save()
    return org


class Organization(models.Model):
  objects = OrganizationManager()

  name = models.CharField(max_length=255, unique=True, error_messages={
    'unique': ('An organization with this name is already in the system. '
    'To add a separate org with the same name, add/alter the name to '
    'differentiate the two.')})
  # email corresponds to User.username
  email = models.EmailField(max_length=100, verbose_name='Login',
                            blank=True, unique=True)
  user = models.OneToOneField(User, null=True)

  # staff entered fields
  staff_contact_person = models.CharField(max_length=250, blank=True,
      verbose_name='Staff-entered contact person')
  staff_contact_person_title = models.CharField(max_length=100, blank=True,
      verbose_name='Title')
  staff_contact_email = models.EmailField(verbose_name='Email address',
      max_length=255, blank=True)
  staff_contact_phone = models.CharField(verbose_name='Phone number',
      max_length=20, blank=True)

  # fields below are autopopulated from the most recent grant application
  # see GrantApplication.save

  # contact info
  address = models.CharField(max_length=100, blank=True)
  city = models.CharField(max_length=50, blank=True)
  state = models.CharField(max_length=2, choices=gc.STATE_CHOICES, blank=True)
  zip = models.CharField(max_length=50, blank=True)
  telephone_number = models.CharField(max_length=20, blank=True)
  fax_number = models.CharField(max_length=20, blank=True)
  email_address = models.EmailField(max_length=100, blank=True)
  website = models.CharField(max_length=50, blank=True)
  contact_person = models.CharField(max_length=250, blank=True,
      verbose_name='Contact person')
  contact_person_title = models.CharField(max_length=100, blank=True,
      verbose_name='Title')

  # org info
  status = models.CharField(max_length=50, choices=gc.STATUS_CHOICES, blank=True)
  ein = models.CharField(max_length=50, blank=True,
      verbose_name="Organization's or Fiscal Sponsor Organization's EIN")
  founded = models.PositiveIntegerField(null=True, blank=True,
                                        verbose_name='Year founded')
  mission = models.TextField(blank=True)

  # fiscal sponsor info (if applicable)
  fiscal_org = models.CharField(verbose_name='Organization name',
                                max_length=255, blank=True)
  fiscal_person = models.CharField(verbose_name='Contact person',
                                   max_length=255, blank=True)
  fiscal_telephone = models.CharField(verbose_name='Telephone',
                                      max_length=25, blank=True)
  fiscal_email = models.CharField(verbose_name='Email address',
                                  max_length=100, blank=True)
  fiscal_address = models.CharField(verbose_name='Address',
                                    max_length=255, blank=True)
  fiscal_city = models.CharField(verbose_name='City',
                                 max_length=50, blank=True)
  fiscal_state = models.CharField(verbose_name='State', max_length=2,
                                  choices=gc.STATE_CHOICES, blank=True)
  fiscal_zip = models.CharField(verbose_name='ZIP', max_length=50, blank=True)
  fiscal_letter = models.FileField(upload_to='/', null=True, blank=True, max_length=255)

  class Meta:
    ordering = ['name']

  def __unicode__(self):
    return self.name

  @staticmethod
  def get_profile_fields():
    return [
      'address', 'city', 'state', 'zip', 'telephone_number', 'fax_number',
      'email_address', 'website', 'contact_person', 'contact_person_title',
      'status', 'ein', 'founded', 'mission', 'fiscal_org', 'fiscal_person',
      'fiscal_telephone', 'fiscal_email', 'fiscal_address', 'fiscal_city',
      'fiscal_state', 'fiscal_zip', 'fiscal_letter'
    ]

  def get_staff_entered_contact_info(self):
    return ', '.join([val for val in [
      self.staff_contact_person, self.staff_contact_person_title,
      self.staff_contact_phone, self.staff_contact_email
    ] if val])

  def update_profile(self, app):
    for field in self.get_profile_fields():
      if hasattr(app, field):
        setattr(self, field, getattr(app, field))
    self.save()
    logger.info('org profile updated - %s', self.name)


class GrantCycle(models.Model):
  title = models.CharField(max_length=100)
  open = models.DateTimeField()
  close = models.DateTimeField()
  extra_question = models.TextField(blank=True)
  info_page = models.URLField()
  email_signature = models.TextField(blank=True)
  conflicts = models.TextField(blank=True,
      help_text='Track any conflicts of interest (automatic & personally '
      'declared) that occurred  during this cycle.')
  private = models.BooleanField(default=False,
      verbose_name='Private (will not be displayed to orgs, but can be '
      'accessed by anyone who has the direct link)')
  two_year_grants = models.BooleanField(default=False,
      help_text='Cycles associated with two-year grants have an extra '
      'question in their application.')
  two_year_question = models.TextField(blank=True,
      default='This grant will provide funding for two years. While we know it can be '
      'difficult to predict your work beyond a year, please give us an idea of '
      'what the second year might look like.<ol><li>What overall goals and '
      'strategies do you forecast in the second year?</li><li>How will the '
      'second year of this grant build on your work in the first year?</li></ol>',
      help_text='Only shown if "Two year grants" is checked. HTML can be used '
      'for formatting')

  class Meta:
    ordering = ['-close', 'title']

  def __unicode__(self):
    return self.title

  def is_open(self):
    return self.open < timezone.now() < self.close

  def get_status(self):
    today = timezone.now()
    if self.close < today:
      return 'closed'
    elif self.open > today:
      return 'upcoming'
    else:
      return 'open'


class DraftGrantApplication(models.Model):
  """ Autosaved draft application """

  organization = models.ForeignKey(Organization)
  grant_cycle = models.ForeignKey(GrantCycle)
  created = models.DateTimeField(blank=True, default=timezone.now)
  modified = models.DateTimeField(blank=True, default=timezone.now)
  modified_by = models.CharField(blank=True, max_length=100)

  contents = models.TextField(default='{}') # json'd dictionary of form contents

  demographics = models.FileField(upload_to='/', max_length=255)
  funding_sources = models.FileField(upload_to='/', max_length=255)
  budget1 = models.FileField(upload_to='/', max_length=255,
                             verbose_name='Annual statement')
  budget2 = models.FileField(upload_to='/', max_length=255,
                             verbose_name='Annual operating budget')
  budget3 = models.FileField(upload_to='/', max_length=255,
                             verbose_name='Balance sheet')
  project_budget_file = models.FileField(upload_to='/', max_length=255,
                                         verbose_name='Project budget')
  fiscal_letter = models.FileField(upload_to='/', max_length=255)

  extended_deadline = models.DateTimeField(blank=True, null=True,
      help_text='Allows this draft to be edited/submitted past the grant cycle close.')

  class Meta:
    unique_together = ('organization', 'grant_cycle')

  @classmethod
  def file_fields(cls):
    return [f.name for f in cls._meta.fields if isinstance(f, models.FileField)]

  def __unicode__(self):
    return u'DRAFT: ' + self.organization.name + ' - ' + self.grant_cycle.title

  def editable(self):
    deadline = self.grant_cycle.close
    logger.debug('deadline is ' + str(self.grant_cycle.close))
    now = timezone.now()
    return (self.grant_cycle.open < now and deadline > now or
           (self.extended_deadline and self.extended_deadline > now))

  def overdue(self):
    return self.grant_cycle.close <= timezone.now()

  def recently_edited(self):
    return timezone.now() < self.modified + timedelta(seconds=35)


class WordLimitValidator(BaseValidator):
  """ Custom validator that checks number of words in a string """
  message = (u'This field has a maximum word count of %(limit_value)d '
              '(current count: %(show_value)d)')
  code = 'max_words'

  def compare(self, count_a, count_b):
    return count_a > count_b

  def clean(self, val):
    return len(unicode(val).translate({ord(c): None for c in string.punctuation}).split())


def validate_file_extension(value):
  """ Method to validate extension of uploaded files
      (Before I knew how to create a validator like the one above) """
  if not value.name.lower().split(".")[-1] in gc.ALLOWED_FILE_TYPES:
    raise ValidationError(u'That file type is not supported.')

class GrantApplication(models.Model):
  """ Submitted grant application """

  # automated fields
  submission_time = models.DateTimeField(blank=True, default=timezone.now,
                                         verbose_name='Submitted')
  organization = models.ForeignKey(Organization)
  grant_cycle = models.ForeignKey(GrantCycle)

  # contact info
  address = models.CharField(max_length=100)
  city = models.CharField(max_length=50)
  state = models.CharField(max_length=2, choices=gc.STATE_CHOICES)
  zip = models.CharField(max_length=50)
  telephone_number = models.CharField(max_length=20)
  fax_number = models.CharField(max_length=20, blank=True,
      verbose_name='Fax number (optional)',
      error_messages={
        'invalid': u'Enter a 10-digit fax number (including area code).'
      })
  email_address = models.EmailField(max_length=100)
  website = models.CharField(max_length=50, blank=True,
                             verbose_name='Website (optional)')

  # org info
  status = models.CharField(max_length=50, choices=gc.STATUS_CHOICES)
  ein = models.CharField(max_length=50,
                         verbose_name="Organization or Fiscal Sponsor EIN")
  founded = models.PositiveIntegerField(verbose_name='Year founded')
  mission = models.TextField(verbose_name="Mission statement",
                             validators=[WordLimitValidator(150)])
  previous_grants = models.CharField(max_length=255, blank=True,
      verbose_name='Previous SJF grants awarded (amounts and year)')

  # budget info
  start_year = models.CharField(max_length=250,
                                verbose_name='Start date of fiscal year')
  budget_last = models.PositiveIntegerField(verbose_name='Org. budget last fiscal year')
  budget_current = models.PositiveIntegerField(verbose_name='Org. budget this fiscal year')

  # this grant info
  grant_request = models.TextField(verbose_name="Briefly summarize the grant request",
                                   validators=[WordLimitValidator(100)])
  contact_person = models.CharField(max_length=250, verbose_name='Name',
                                    help_text='Contact person for this grant application')
  contact_person_title = models.CharField(max_length=100, verbose_name='Title')
  grant_period = models.CharField(max_length=250, blank=True,
                                  verbose_name='Grant period (if different than fiscal year)')
  amount_requested = models.PositiveIntegerField()

  SUPPORT_CHOICES = [('General support', 'General support'),
                     ('Project support', 'Project support')]
  support_type = models.CharField(max_length=50, choices=SUPPORT_CHOICES, default='General support')
  project_title = models.CharField(max_length=250, blank=True,
                                   verbose_name='Project title (if applicable)')
  project_budget = models.PositiveIntegerField(null=True, blank=True,
                                               verbose_name='Project budget (if applicable)')

  # fiscal sponsor
  fiscal_org = models.CharField(verbose_name='Fiscal org. name',
                                max_length=255, blank=True)
  fiscal_person = models.CharField(verbose_name='Contact person',
                                   max_length=255, blank=True)
  fiscal_telephone = models.CharField(verbose_name='Telephone',
                                      max_length=25, blank=True)
  fiscal_email = models.CharField(verbose_name='Email address',
                                  max_length=70, blank=True)
  fiscal_address = models.CharField(verbose_name='Address',
                                    max_length=255, blank=True)
  fiscal_city = models.CharField(verbose_name='City', max_length=50, blank=True)
  fiscal_state = models.CharField(verbose_name='State', max_length=2,
                                  choices=gc.STATE_CHOICES, blank=True)
  fiscal_zip = models.CharField(verbose_name='ZIP', max_length=50, blank=True)

  narrative1 = models.TextField(verbose_name=gc.NARRATIVE_TEXTS['narrative1'],
      validators=[WordLimitValidator(gc.NARRATIVE_WORD_LIMITS['narrative1'])])
  narrative2 = models.TextField(verbose_name=gc.NARRATIVE_TEXTS['narrative2'],
      help_text=gc.HELP_TEXTS['leadership'],
      validators=[WordLimitValidator(gc.NARRATIVE_WORD_LIMITS['narrative2'])])
  narrative3 = models.TextField(verbose_name=gc.NARRATIVE_TEXTS['narrative3'],
      validators=[WordLimitValidator(gc.NARRATIVE_WORD_LIMITS['narrative3'])])
  narrative4 = models.TextField(verbose_name=gc.NARRATIVE_TEXTS['narrative4'],
      validators=[WordLimitValidator(gc.NARRATIVE_WORD_LIMITS['narrative4'])],
      help_text=gc.HELP_TEXTS['goals'])
  narrative5 = models.TextField(verbose_name=gc.NARRATIVE_TEXTS['narrative5'],
      validators=[WordLimitValidator(gc.NARRATIVE_WORD_LIMITS['narrative5'])])
  narrative6 = models.TextField(verbose_name=gc.NARRATIVE_TEXTS['narrative6'],
      validators=[WordLimitValidator(gc.NARRATIVE_WORD_LIMITS['narrative6'])],
      help_text=gc.HELP_TEXTS['leadership'])
  cycle_question = models.TextField(blank=True,
      validators=[WordLimitValidator(gc.NARRATIVE_WORD_LIMITS['cycle_question'])])

  timeline = models.TextField(verbose_name=gc.NARRATIVE_TEXTS['timeline'])

  # collab references (after narrative 5)
  collab_ref1_name = models.CharField(verbose_name='Name', max_length=150,
      help_text=('Provide names and contact information for two people who '
                 'are familiar with your organization\'s role in these '
                 'collaborations so we can contact them for more information.'))
  collab_ref1_org = models.CharField(verbose_name='Organization',
                                     max_length=150)
  collab_ref1_phone = models.CharField(verbose_name='Phone number',
                                       max_length=20, blank=True)
  collab_ref1_email = models.EmailField(max_length=100, verbose_name='Email',
                                        blank=True)

  collab_ref2_name = models.CharField(verbose_name='Name', max_length=150)
  collab_ref2_org = models.CharField(verbose_name='Organization',
                                     max_length=150)
  collab_ref2_phone = models.CharField(verbose_name='Phone number',
                                       max_length=20, blank=True)
  collab_ref2_email = models.EmailField(max_length=100, verbose_name='Email',
                                        blank=True)

  # racial justice references (after narrative 6)
  racial_justice_ref1_name = models.CharField(
      verbose_name='Name', max_length=150, blank=True)
  racial_justice_ref1_org = models.CharField(
      verbose_name='Organization', max_length=150, blank=True)
  racial_justice_ref1_phone = models.CharField(
      verbose_name='Phone number', max_length=20, blank=True)
  racial_justice_ref1_email = models.EmailField(
      verbose_name='Email', max_length=100, blank=True)

  racial_justice_ref2_name = models.CharField(verbose_name='Name',
                                              max_length=150, blank=True)
  racial_justice_ref2_org = models.CharField(verbose_name='Organization',
                                             max_length=150, blank=True)
  racial_justice_ref2_phone = models.CharField(verbose_name='Phone number',
                                               max_length=20, blank=True)
  racial_justice_ref2_email = models.EmailField(verbose_name='Email',
                                                max_length=100, blank=True)

  # files
  budget = models.FileField( # no longer shown, but field holds file from early apps
      upload_to='/', max_length=255, validators=[validate_file_extension], blank=True)
  demographics = models.FileField(
      verbose_name='Diversity chart', upload_to='/', max_length=255,
      validators=[validate_file_extension])
  funding_sources = models.FileField(upload_to='/', max_length=255,
      validators=[validate_file_extension])
  budget1 = models.FileField(
      verbose_name='Annual statement', upload_to='/', max_length=255,
      validators=[validate_file_extension],
      help_text=('This is the statement of actual income and expenses for '
                   'the most recent completed fiscal year. Upload in your own '
                   'format, but do not send your annual report, tax returns, '
                   'or entire audited financial statement.'))
  budget2 = models.FileField(
      verbose_name='Annual operating budget', upload_to='/', max_length=255,
      validators=[validate_file_extension],
      help_text=('This is a projection of all known and estimated income and '
                   'expenses for the current fiscal year. You may upload in '
                   'your own format or use our budget form. NOTE: If your '
                   'fiscal year will end within three months of this grant '
                   'application deadline, please also attach your operating '
                   'budget for the next fiscal year, so that we can get a more '
                   'accurate sense of your organization\'s situation.'))
  budget3 = models.FileField(
      verbose_name='Balance sheet', upload_to='/', max_length=255,
      validators=[validate_file_extension],
      help_text=('This is a snapshot of your financial status at the moment: '
                   'a brief, current statement of your assets, liabilities, '
                   'and cash on hand. Upload in your own format.'))
  project_budget_file = models.FileField(
      verbose_name='Project budget (if applicable)', upload_to='/',
      max_length=255, validators=[validate_file_extension], blank=True,
      help_text=('This is required only if you are requesting '
                   'project-specific funds. Otherwise, it is optional. You '
                   'may upload in your own format or use our budget form.'))
  fiscal_letter = models.FileField(
      upload_to='/', blank=True, verbose_name='Fiscal sponsor letter',
      help_text=('Letter from the sponsor stating that it agrees to act as your '
                 'fiscal sponsor and supports Social Justice Fund\'s mission.'),
      max_length=255, validators=[validate_file_extension])

  # admin fields
  pre_screening_status = models.IntegerField(choices=gc.PRE_SCREENING, default=10)
  giving_projects = models.ManyToManyField(GivingProject, through='ProjectApp', blank=True)
  scoring_bonus_poc = models.BooleanField(default=False,
      verbose_name='Scoring bonus for POC-led')
  scoring_bonus_geo = models.BooleanField(default=False,
      verbose_name='Scoring bonus for geographic diversity')
  site_visit_report = models.URLField(
      blank=True, help_text=('Link to the google doc containing the site '
      'visit report. This will be visible to all project members, but not the '
      'organization.'))

  class Meta:
    ordering = ['organization', 'submission_time']
    unique_together = ('organization', 'grant_cycle')

  @classmethod
  def fields_starting_with(cls, start):
    return [f for f in cls._meta.get_all_field_names() if f.startswith(start)]

  @classmethod
  def file_fields(cls):
    return [f.name for f in cls._meta.fields if isinstance(f, models.FileField)]

  @classmethod
  def get_field_names(cls):
    return [f for f in cls._meta.get_all_field_names()]

  def __unicode__(self):
    return '%s - %s' % (unicode(self.organization), unicode(self.grant_cycle))

  def get_file_name(self, field_name):
    file_attr = getattr(self, field_name)
    if file_attr and hasattr(file_attr, 'name'):
      file_info = file_attr.name.split('/', 1)
      if len(file_info) > 1:
        return file_info[1]
      else:
        return file_attr.name
    return ''

  def save(self, *args, **kwargs):
    """ Update org profile if it is the most recent app for the org """

    super(GrantApplication, self).save(*args, **kwargs)

    # check if there are more recent apps
    apps = GrantApplication.objects.filter(organization_id=self.organization_id,
                                           submission_time__gt=self.submission_time)

    if apps.exists():
      logger.info('App updated, not the most recent for org, regular save')
    else:
      logger.info('App updated, is most recent, updating org profile')
      self.organization.update_profile(self)

  def timeline_display(self):
    # TODO clean this up
    timeline = json.loads(self.timeline)
    html = ('<table id="timeline_display">'
            '<tr class="heading">'
            '<td></td>'
            '<th>date range</th>'
            '<th>activities</th>'
            '<th>goals/objectives</th>'
            '</tr>')
    row = u'<tr><th class="left">q{}</th><td>{}</td><td>{}</td><td>{}</td></tr>'
    for i in range(0, 15, 3):
      q = i/3 + 1
      colA = timeline[i] if len(timeline) > i else ''
      colB = timeline[i + 1] if len(timeline) > i + 1 else ''
      colC = timeline[i + 2] if len(timeline) > i + 2 else ''
      html += row.format(q, colA, colB, colC)
    html += '</table>'
    return html
  timeline_display.allow_tags = True


class GrantApplicationOverflow(models.Model): # pylint: disable=model-missing-unicode

  grant_application = models.OneToOneField(GrantApplication, related_name='overflow')
  two_year_question = models.TextField(blank=True,
      validators=[WordLimitValidator(gc.NARRATIVE_WORD_LIMITS['two_year_question'])])


class ProjectApp(models.Model):
  """ Connection between a grant app and a giving project.

  Stores that project's screening and site visit info related to the app """

  giving_project = models.ForeignKey(GivingProject)
  application = models.ForeignKey(GrantApplication)

  screening_status = models.IntegerField(choices=gc.SCREENING, blank=True, null=True)

  class Meta:
    unique_together = ('giving_project', 'application')

  def __unicode__(self):
    return '%s - %s' % (self.giving_project.title, self.application)


class GrantApplicationLog(models.Model):
  date = models.DateTimeField(default=timezone.now)
  organization = models.ForeignKey(Organization)
  application = models.ForeignKey(GrantApplication, null=True, blank=True,
      help_text=('Optional - if this log entry relates to a specific grant '
                 'application, select it from the list'))
  staff = models.ForeignKey(User)
  contacted = models.CharField(max_length=255, blank=True,
      help_text='Person from the organization that you talked to, if applicable.')
  notes = models.TextField()

  class Meta:
    ordering = ['-date']

  def __unicode__(self):
    return 'Log entry from {:%m/%d/%y}'.format(self.date)


class GivingProjectGrant(models.Model):
  created = models.DateTimeField(default=timezone.now)

  projectapp = models.OneToOneField(ProjectApp)

  amount = models.DecimalField(max_digits=8, decimal_places=2)
  check_number = models.PositiveIntegerField(null=True, blank=True)
  check_mailed = models.DateField(null=True, blank=True)

  second_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
  second_check_number = models.PositiveIntegerField(null=True, blank=True)
  second_check_mailed = models.DateField(null=True, blank=True)

  agreement_mailed = models.DateField(null=True, blank=True)
  agreement_returned = models.DateField(null=True, blank=True)
  approved = models.DateField(verbose_name='Date approved by the ED', null=True, blank=True)

  first_yer_due = models.DateField(
      verbose_name='Year-end report due date',
      help_text='If this is a two-year grant, the second YER will '
                'automatically be due one year after the first')

  class Meta:
    ordering = ['-created']

  def __unicode__(self):
    """ Basic description of grant: amount and duration """
    summary = u'${:,} '
    if self.grant_length() == 2:
      summary += 'two-year '
    summary += 'grant'
    return summary.format(self.total_amount())

  def full_description(self):
    """ Description of grant including the giving project that made the award.
        Not used as __unicode__ since it may trigger additional DB lookups """
    return u'{} from {}'.format(self, self.projectapp.giving_project)

  def agreement_due(self):
    """ Agreement is due 30 days after it is mailed
      Returns datetime.date or None if agreement has not been mailed
    """
    if self.agreement_mailed:
      return self.agreement_mailed + timedelta(days=30)
    else:
      return None

  def next_yer_due(self):
    """ Year-end reports are due n year(s) after agreement was mailed
      Returns datetime.date or None if all YER have been submitted for this grant
    """
    completed = self.yearendreport_set.count()
    if completed >= self.grant_length():
      return None
    else:
      return self.first_yer_due.replace(year=self.first_yer_due.year + completed)

  def total_amount(self):
    """ Total amount granted, or 0 if no amount has been entered """
    first_amount = self.amount or 0
    if self.second_amount:
      return self.second_amount + first_amount
    else:
      return first_amount

  def grant_length(self):
    """ Returns length of grant in years. Only supports 1 or 2 year grants """
    return 2 if self.second_amount else 1

  def fully_paid(self):
    if not self.check_mailed:
      return False
    if self.second_amount and not self.second_check_mailed:
      return False
    return True


class SponsoredProgramGrant(models.Model):

  entered = models.DateTimeField(default=timezone.now)
  organization = models.ForeignKey(Organization)
  amount = models.PositiveIntegerField()
  check_number = models.PositiveIntegerField(null=True, blank=True)
  check_mailed = models.DateField(null=True, blank=True)
  approved = models.DateField(verbose_name='Date approved by the ED',
                              null=True, blank=True)
  description = models.TextField(blank=True)

  class Meta:
    ordering = ['organization']

  def __unicode__(self):
    desc = 'Sponsored program grant - {}'.format(self.organization)
    if self.approved:
      desc += ' - {:%m/%d/%Y}'.format(self.approved)
    return desc


def validate_photo_file_extension(value):
  """ Method to validate file extension of uploaded photos.
      (Should probably be custom validator) """
  if not value.name.lower().split('.')[-1] in gc.PHOTO_FILE_TYPES:
    raise ValidationError(u'That file type is not supported. Please upload an '
        'image with one of these extensions: %s' % ', '.join(gc.PHOTO_FILE_TYPES))


class YearEndReport(models.Model):
  award = models.ForeignKey(GivingProjectGrant)
  submitted = models.DateTimeField(default=timezone.now)

  # user-entered
  contact_person = models.TextField() # Name, title (has custom widget)
  email = models.EmailField(max_length=255)
  phone = models.CharField(max_length=20)
  website = models.CharField(max_length=255) # autofill based on app

  summarize_last_year = models.TextField(verbose_name=(
      '1. Thinking about the Giving Project volunteers who decided to fund '
      'you last year, including those you met on your site visit, what would '
      'you like to tell them about what you\'ve done over the last year?'))
  goal_progress = models.TextField(verbose_name=(
      '2. Please refer back to your application from last year. Looking at '
      'the goals you outlined in your application, what progress have you '
      'made on each? If you were unable to achieve those goals or changed '
      'your direction, please explain why.'))
  quantitative_measures = models.TextField(verbose_name=(
      '3. Do you evaluate your work by any quantitative measures (e.g., number '
      'of voters registered, members trained, leaders developed, etc.)? If '
      'so, provide that information:'), blank=True)
  evaluation = models.TextField(verbose_name=(
      '4. What other type of evaluations do you use internally? Please share '
      'any outcomes that are relevant to the work funded by this grant.'))
  achieved = models.TextField(verbose_name=(
      '5. What specific victories, benchmarks, and/or policy changes (local, '
      'state, regional, or national) have you achieved over the past year?'))
  collaboration = models.TextField(verbose_name=(
      '6. What other organizations did you work with to achieve those '
      'accomplishments?'))
  new_funding = models.TextField(verbose_name=(
      '7. Did your grant from Social Justice Fund help you access any new '
      'sources of funding? If so, please explain.'), blank=True)
  major_changes = models.TextField(verbose_name=(
      '8. Describe any major staff or board changes or other major '
      'organizational changes in the past year.'), blank=True)
  total_size = models.PositiveIntegerField(verbose_name=(
      '9. What is the total size of your base? That is, how many people, '
      'including paid staff, identify as part of your organization?'))
  donations_count = models.PositiveIntegerField(verbose_name=(
      '10. How many individuals gave a financial contribution of any size to '
      'your organization in the last year?'))
  donations_count_prev = models.PositiveIntegerField(null=True, verbose_name=(
      'How many individuals made a financial contribution the previous year?'))

  stay_informed = models.TextField(verbose_name=(
    '11. What is the best way for us to stay informed about your work? '
    '(Enter any/all that apply)'), default='{}')

  other_comments = models.TextField(verbose_name=(
    '12. Other comments or information? Do you have any suggestions for how '
    'SJF can improve its grantmaking programs?'), blank=True) # json dict - see modelforms

  photo1 = models.FileField(validators=[validate_photo_file_extension],
      upload_to='/', max_length=255,
      help_text=('Please provide two or more photos that show your '
                 'organization\'s members, activities, etc. These pictures '
                 'help us tell the story of our grantees and of Social Justice '
                 'Fund to the broader public.'))
  photo2 = models.FileField(validators=[validate_photo_file_extension],
      upload_to='/', max_length=255)
  photo3 = models.FileField(validators=[validate_photo_file_extension],
      upload_to='/', help_text='(optional)', blank=True, max_length=255)
  photo4 = models.FileField(validators=[validate_photo_file_extension],
      upload_to='/', help_text='(optional)', blank=True, max_length=255)

  photo_release = models.FileField(upload_to='/', max_length=255,
    verbose_name=('Please provide photo releases signed by any people who '
                  'appear in these photos.'))

  # admin-entered
  visible = models.BooleanField(default=False, help_text=('Check this to make '
      'the YER visible to members of the GP that made the grant. (When '
      'unchecked, YER is only visible to staff and the org that submitted it.)'))

  def __unicode__(self):
    return 'Year-end report for ' + unicode(self.award)

  def stay_informed_display(self):
    display = []
    inf = json.loads(self.stay_informed)
    for key in inf:
      value = inf[key]
      if value:
        display.append(key + ': ' + value)
    return ', '.join(display)


class YERDraft(models.Model):

  award = models.ForeignKey(GivingProjectGrant)
  modified = models.DateTimeField(default=timezone.now)
  contents = models.TextField(default='{}')

  photo1 = models.FileField(upload_to='/', blank=True, max_length=255)
  photo2 = models.FileField(upload_to='/', blank=True, max_length=255)
  photo3 = models.FileField(upload_to='/', blank=True, max_length=255)
  photo4 = models.FileField(upload_to='/', blank=True, max_length=255)

  photo_release = models.FileField(upload_to='/', max_length=255)

  class Meta:
    verbose_name = 'Draft year-end report'

  def __unicode__(self):
    return 'DRAFT year-end report for ' + unicode(self.award)
