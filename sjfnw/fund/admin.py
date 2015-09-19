import datetime, logging, json

from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponse
from django.utils import timezone
from django.utils.safestring import mark_safe

from libs import unicodecsv

from sjfnw import utils
from sjfnw.admin import advanced_admin
from sjfnw.fund.models import (GivingProject, Member, Membership, Survey,
    GPSurvey, Resource, ProjectResource, Donor, Step, NewsItem, SurveyResponse)
from sjfnw.fund import forms, utils as fund_utils, modelforms
from sjfnw.grants.models import ProjectApp, GrantApplication

logger = logging.getLogger('sjfnw')

# -----------------------------------------------------------------------------
# Filters
# -----------------------------------------------------------------------------

class PromisedBooleanFilter(SimpleListFilter):
  """ Filter by promised field """
  title = 'promised'
  parameter_name = 'promised_tf'

  def lookups(self, request, model_admin):
    return (('True', 'Promised'),
            ('False', 'Declined'),
            ('None', 'None entered'))

  def queryset(self, request, queryset):
    if self.value() == 'True':
      return queryset.filter(promised__gt=0)
    if self.value() == 'False':
      return queryset.filter(promised=0)
    elif self.value() == 'None':
      return queryset.filter(promised__isnull=True)


class ReceivedBooleanFilter(SimpleListFilter):
  """ Filter by received (any of received_this, _next, _afternext) """
  title = 'received'
  parameter_name = 'received_tf'

  def lookups(self, request, model_admin):
    return (('True', 'Gift received'), ('False', 'No gift received'))

  def queryset(self, request, queryset):
    if self.value() == 'True':
      return queryset.exclude(
          received_this=0, received_next=0, received_afternext=0)
    if self.value() == 'False':
      return queryset.filter(
          received_this=0, received_next=0, received_afternext=0)


class GPYearFilter(SimpleListFilter):
  """ Filter giving projects by year """
  title = 'year'
  parameter_name = 'year'

  def lookups(self, request, model_admin):
    deadlines = (GivingProject.objects.values_list('fundraising_deadline', flat=True)
                                      .order_by('-fundraising_deadline'))
    prev = None
    years = []
    for deadline in deadlines:
      if deadline.year != prev:
        years.append((deadline.year, deadline.year))
        prev = deadline.year
    return years

  def queryset(self, request, queryset):
    val = self.value()
    if not val:
      return queryset
    try:
      year = int(val)
    except ValueError:
      logger.error('GPYearFilter received invalid value %s', val)
      messages.error(request,
          'Error loading filter. Contact techsupport@socialjusticefund.org')
      return queryset
    return queryset.filter(fundraising_deadline__year=year)

# -----------------------------------------------------------------------------
# Inlines
# -----------------------------------------------------------------------------

class MembershipInline(admin.TabularInline):
  model = Membership
  formset = forms.MembershipInlineFormset
  extra = 0
  can_delete = False
  fields = ['member', 'giving_project', 'approved', 'leader']

  def formfield_for_foreignkey(self, db_field, request, **kwargs):

    # cache member choices to reduce queries
    if db_field.name == 'member':

      cached_choices = getattr(request, 'cached_members', None)
      if cached_choices:
        logger.debug('Using cached choices for membership inline')
        formfield = super(MembershipInline, self).formfield_for_foreignkey(
            db_field, request, **kwargs)
        formfield.choices = cached_choices

      else:
        members = Member.objects.all()
        formfield = super(MembershipInline, self).formfield_for_foreignkey(
            db_field, request, **kwargs)
        formfield.choices = [(member.pk, unicode(member)) for member in members]
        request.cached_members = formfield.choices

      return formfield

    else: # different field
      return super(MembershipInline, self).formfield_for_foreignkey(
          db_field, request, **kwargs)


class ProjectResourcesInline(admin.TabularInline):
  model = ProjectResource
  extra = 0
  template = 'admin/fund/projectresource/tabular_inline.html'
  fields = ['resource', 'session']


class DonorInline(admin.TabularInline):
  model = Donor
  extra = 0
  max_num = 0
  can_delete = False
  readonly_fields = ['firstname', 'lastname', 'amount', 'talked', 'asked',
                     'promised', 'total_promised']
  fields = ['firstname', 'lastname', 'amount', 'talked', 'asked', 'promised']


class ProjectAppInline(admin.TabularInline):
  model = ProjectApp
  extra = 1
  verbose_name = 'Grant application'
  verbose_name_plural = 'Grant applications'
  fields = ['application', 'app_link', 'screening_status', 'grant_link']
  readonly_fields = ['app_link', 'grant_link']

  def get_queryset(self, request):
    return super(ProjectAppInline, self).get_queryset(request).select_related(
        'application', 'givingprojectgrant')

  def app_link(self, obj):
    if obj and hasattr(obj, 'application'):
      return utils.create_link(
        '/admin/grants/grantapplication/{}/'.format(obj.application.pk),
        'View application')
    else:
      return ''
  app_link.allow_tags = True

  def grant_link(self, obj):
    if obj:
      if hasattr(obj, 'givingprojectgrant'):
        return utils.create_link(
          '/admin/grants/givingprojectgrant/{}/'.format(obj.givingprojectgrant.pk),
          'View grant')

      if hasattr(obj, 'screening_status') and obj.screening_status > 80:
        return utils.create_link(
          '/admin/grants/givingprojectgrant/add/?projectapp={}'.format(obj.pk),
          'Add grant')
    else:
      return ''
  grant_link.allow_tags = True

  def formfield_for_foreignkey(self, db_field, request, **kwargs):
    """ Limit application dropdown choices based on GP fundraising deadline

      Otherwise we may get 'response too large' error
    """
    formfield = super(ProjectAppInline, self).formfield_for_foreignkey(
        db_field, request, **kwargs)

    if db_field.name == 'application':
      apps = GrantApplication.objects.select_related('grant_cycle', 'organization')
      try:
        gp_id = int(request.path.split('/')[-2])
      except ValueError:
        # this shoudn't be possible, but just to be safe
        # (it shouuld 404 if url doesn't match expected pattern)
        logger.error('Could not parse GP id. URL: %s', request.path)
        raise
      else:
        gp = GivingProject.objects.get(pk=gp_id)
        year = gp.fundraising_deadline - datetime.timedelta(weeks=52)
        apps = apps.filter(submission_time__gte=year)
        # create choices from queryset
        formfield.choices = [('', '---------')] + [(app.pk, unicode(app)) for app in apps]

    return formfield


class GPSurveyI(admin.TabularInline):
  model = GPSurvey
  extra = 1
  verbose_name = 'Survey'
  verbose_name_plural = 'Surveys'

  def get_queryset(self, request):
    return super(GPSurveyI, self).get_queryset(request).select_related('survey')

# -----------------------------------------------------------------------------
# ModelAdmin
# -----------------------------------------------------------------------------

class GivingProjectA(admin.ModelAdmin):
  list_display = ['title', 'gp_year', 'estimated']
  list_filter = [GPYearFilter]
  fields = [
    ('title', 'public'),
    ('fundraising_training', 'fundraising_deadline'),
    'fund_goal', 'site_visits', 'calendar', 'suggested_steps', 'pre_approved'
  ]
  readonly_fields = ['estimated']
  form = modelforms.GivingProjectAdminForm
  inlines = [GPSurveyI, ProjectResourcesInline, MembershipInline, ProjectAppInline]

  def gp_year(self, obj):
    year = obj.fundraising_deadline.year
    if year == timezone.now().year:
      return '<b>%d</b>' % year
    else:
      return year
  gp_year.short_description = 'Year'
  gp_year.allow_tags = True


class ResourceA(admin.ModelAdmin):
  list_display = ['title', 'created']
  fields = ['title', 'summary', 'link']


class MemberAdvanced(admin.ModelAdmin):
  list_display = ['first_name', 'last_name', 'email']
  search_fields = ['first_name', 'last_name', 'email']


class MembershipA(admin.ModelAdmin):
  actions = ['approve']
  search_fields = ['member__first_name', 'member__last_name']
  list_display = [
    'member', 'giving_project', 'ship_progress', 'overdue_steps', 'last_activity',
    'approved', 'leader'
  ]
  list_filter = ['approved', 'leader', 'giving_project']
  readonly_list = ['ship_progress', 'overdue_steps']

  fields = [
    ('member', 'giving_project', 'approved'),
    ('leader', 'last_activity', 'emailed'),
    ('ship_progress'),
    'notifications'
  ]
  readonly_fields = ['last_activity', 'emailed', 'ship_progress']
  inlines = [DonorInline]

  def approve(self, _, queryset):
    for memship in queryset:
      if memship.approved == False:
        fund_utils.NotifyApproval(memship)
    queryset.update(approved=True)

  def ship_progress(self, obj):
    progress = obj.get_progress()
    return ('<table class="nested-column nested-column-4"><tr><td>${estimated}</td>'
            '<td>${promised}</td><td>${received_total}</td>'
            '<td>{received_this}, {received_next}, {received_afternext}</td>'
            '</tr></table>').format(**progress)
  ship_progress.short_description = mark_safe(
      '<table class="nested-column-4"><tr><td>Estimated</td><td>Total promised</td>'
      '<td>Received</td><td>Rec. by year</td></tr></table>')
  ship_progress.allow_tags = True


class DonorA(admin.ModelAdmin):
  list_display = ['firstname', 'lastname', 'membership', 'amount', 'talked',
                  'asked', 'total_promised', 'received_this', 'received_next',
                  'received_afternext', 'match_expected', 'match_received']
  list_filter = ['membership__giving_project', 'asked', PromisedBooleanFilter,
                 ReceivedBooleanFilter]
  list_editable = ['received_this', 'received_next', 'received_afternext',
                   'match_expected', 'match_received']
  search_fields = ['firstname', 'lastname', 'membership__member__first_name',
                   'membership__member__last_name']
  actions = ['export_donors']

  fields = [
    'membership',
    ('firstname', 'lastname'),
    ('phone', 'email'),
    ('amount', 'likelihood'),
    ('talked', 'asked', 'promised', 'promise_reason_display', 'likely_to_join'),
    ('received_this', 'received_next', 'received_afternext'),
    ('match_expected', 'match_company', 'match_received'),
    'notes'
  ]
  readonly_fields = ['promise_reason_display', 'likely_to_join']

  def export_donors(self, request, queryset):
    logger.info('Export donors called by ' + request.user.email)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=prospects.csv'
    writer = unicodecsv.writer(response)

    writer.writerow(['First name', 'Last name', 'Phone', 'Email', 'Member',
                     'Giving Project', 'Amount to ask', 'Asked', 'Promised',
                     'Received - TOTAL', 'Received - Year', 'Received - Amount',
                     'Received - Year', 'Received - Amount',
                     'Received - Year', 'Received - Amount', 'Notes',
                     'Likelihood of joining a GP', 'Reasons for donating'])
    count = 0
    for donor in queryset:
      year = donor.membership.giving_project.fundraising_deadline.year
      fields = [donor.firstname, donor.lastname, donor.phone, donor.email,
                donor.membership.member, donor.membership.giving_project,
                donor.amount, donor.asked, donor.promised, donor.received(),
                year, donor.received_this, year+1, donor.received_next, year+2,
                donor.received_afternext, donor.notes,
                donor.get_likely_to_join_display(),
                donor.promise_reason_display(), donor.total_promised(),
                donor.match_expected, donor.match_received, donor.match_company]
      writer.writerow(fields)
      count += 1
    logger.info(str(count) + ' donors exported')
    return response


class NewsA(admin.ModelAdmin):
  list_display = ['summary', 'date', 'membership']
  list_filter = ['membership__giving_project']


class StepAdv(admin.ModelAdmin):
  list_display = ['description', 'donor', 'step_membership', 'date',
                  'completed', 'promised']
  list_filter = ['donor__membership', PromisedBooleanFilter,
                 ReceivedBooleanFilter]

  def step_membership(self, obj):
    return obj.donor.membership


class SurveyA(admin.ModelAdmin):
  list_display = ['title', 'updated']
  form = modelforms.CreateSurvey
  fields = ['title', 'intro', 'questions']
  readonly_fields = ['updated']

  def save_model(self, request, obj, form, change):
    obj.updated = timezone.now()
    obj.updated_by = request.user.username
    obj.save()


class SurveyResponseA(admin.ModelAdmin):
  list_display = ['gp_survey', 'date']
  list_filter = ['gp_survey__giving_project']
  fields = ['gp_survey', 'date', 'display_responses']
  readonly_fields = ['gp_survey', 'date', 'display_responses']
  actions = ['export_responses']

  def display_responses(self, obj):
    if obj and obj.responses:
      resp_list = json.loads(obj.responses)
      disp = '<table><tr><th>Question</th><th>Answer</th></tr>'
      for i in range(0, len(resp_list), 2):
        disp += ('<tr><td>' + unicode(resp_list[i]) + '</td><td>' +
                 unicode(resp_list[i+1]) + '</td></tr>')
      disp += '</table>'
      return mark_safe(disp)
  display_responses.short_description = 'Responses'

  def export_responses(self, request, queryset):

    logger.info('Export survey responses called by ' + request.user.email)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = ('attachment; filename=survey_responses %s.csv'
        % timezone.now().strftime('%Y-%m-%d'))
    writer = unicodecsv.writer(response)

    header = ['Date', 'Survey ID', 'Giving Project', 'Survey'] # base
    questions = 0
    response_rows = []
    for survey in queryset:
      fields = [survey.date, survey.gp_survey_id,
                survey.gp_survey.giving_project.title,
                survey.gp_survey.survey.title]
      logger.info(isinstance(survey.responses, str))
      responses = json.loads(survey.responses)
      for i in range(0, len(responses), 2):
        fields.append(responses[i])
        fields.append(responses[i+1])
        questions = max(questions, (i+2)/2)
      response_rows.append(fields)

    logger.info('Max %d questions', questions)
    for i in range(0, questions):
      header.append('Question')
      header.append('Answer')
    writer.writerow(header)
    for row in response_rows:
      writer.writerow(row)

    return response

#------------------------------------------------------------------------------
# Register
#------------------------------------------------------------------------------

admin.site.register(GivingProject, GivingProjectA)
admin.site.register(Membership, MembershipA)
admin.site.register(NewsItem, NewsA)
admin.site.register(Donor, DonorA)
admin.site.register(Resource, ResourceA)
admin.site.register(Survey, SurveyA)
admin.site.register(SurveyResponse, SurveyResponseA)

advanced_admin.register(Member, MemberAdvanced)
advanced_admin.register(Donor, DonorA)
advanced_admin.register(Membership, MembershipA)
advanced_admin.register(GivingProject, GivingProjectA)
advanced_admin.register(NewsItem, NewsA)
advanced_admin.register(Step, StepAdv)
advanced_admin.register(ProjectResource)
advanced_admin.register(Resource, ResourceA)
