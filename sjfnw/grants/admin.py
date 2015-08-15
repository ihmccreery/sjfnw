import logging

from django.contrib import admin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from sjfnw.admin import advanced_admin, YearFilter
from sjfnw.grants import models
from sjfnw.grants.modelforms import DraftAdminForm

logger = logging.getLogger('sjfnw')

#------------------------------------------------------------------------------
# CUSTOM FILTERS
#------------------------------------------------------------------------------

class GrantCycleYearFilter(YearFilter):
  filter_model = models.GrantCycle
  field = 'close'
  intermediate = 'projectapp__application__grant_cycle'
  title = 'Grant cycle year'

class CycleTypeFilter(admin.SimpleListFilter):
  title = 'Grant cycle type'
  parameter_name = 'cycle_type'

  def lookups(self, request, model_admin):
    titles = (models.GrantCycle.objects.values_list('title', flat=True)
                                       .distinct().order_by('title'))
    # group cycles into "types" - criminal justice, economic justice, etc.
    types = []
    for title in titles:
      pos = title.find(' Grant Cycle')
      if pos > 1:
        cycle_type = title[:pos]
        if not cycle_type in types:
          types.append(cycle_type)
      else: # Grant Cycle not found - just use whole
        if not title in types:
          types.append(title)
    return [(t, t) for t in types]

  def queryset(self, request, queryset):
    if not self.value():
      return queryset
    else:
      return queryset.filter(projectapp__application__grant_cycle__title__startswith=self.value())

class MultiYearGrantFilter(admin.SimpleListFilter):
  title = 'Grant length'
  parameter_name = 'multiyear'

  def lookups(self, request, model_admin):
    return [
      (1, 'Single-year'),
      (2, 'Two-year')
    ]

  def queryset(self, request, queryset):
    if self.value() == '1':
      return queryset.filter(second_amount__isnull=True)
    if self.value() == '2':
      return queryset.filter(second_amount__isnull=False)
    return queryset


#------------------------------------------------------------------------------
# INLINES
#------------------------------------------------------------------------------

class BaseShowInline(admin.TabularInline):
  """ Base inline for read only items """
  extra = 0
  max_num = 0
  can_delete = False

  class Meta:
    abstract = True


class LogReadonlyI(admin.TabularInline):
  """ Show existing logs as an inline. Can be deleted but not edited.
      Used by Org, Application """
  model = models.GrantApplicationLog
  extra = 0
  max_num = 0
  fields = ['date', 'grantcycle', 'staff', 'contacted', 'notes']
  readonly_fields = ['date', 'grantcycle', 'staff', 'contacted', 'notes']
  verbose_name = 'Log'
  verbose_name_plural = 'Logs'

  def queryset(self, request):
    qs = super(LogReadonlyI, self).queryset(request)
    return qs.select_related('staff', 'application', 'application__grant_cycle')

  def grantcycle(self, obj):
    if obj.application:
      return obj.application.grant_cycle
    else:
      return ''
  grantcycle.short_description = 'Application' # app is identified by grant cycle in this case


class LogI(admin.TabularInline):
  """ Inline for adding a log to an org or application
      Shows one blank row. Autofills org or app depending on current page """
  model = models.GrantApplicationLog
  extra = 1
  max_num = 1
  can_delete = False
  exclude = ['date',] # auto-populated
  verbose_name_plural = 'Add a log entry'

  def queryset(self, request):
    return models.GrantApplicationLog.objects.none()

  def formfield_for_foreignkey(self, db_field, request, **kwargs):
    """ Give initial values for staff and/or org.
        This is called once on every foreign key field """
    if not '/add' in request.path: # skip when creating new org/app
      # autofill staff field
      if db_field.name == 'staff':
        kwargs['initial'] = request.user.id
        kwargs['queryset'] = User.objects.filter(is_staff=True)
        return db_field.formfield(**kwargs)

      # organization field on app page
      elif 'grantapplication' in request.path and db_field.name == 'organization':
        app_id = int(request.path.split('/')[-2])
        app = models.GrantApplication.objects.get(pk=app_id)
        kwargs['initial'] = app.organization_id
        return db_field.formfield(**kwargs)

      # application field
      if db_field.name == 'application':
        org_pk = int(request.path.split('/')[-2])
        kwargs['queryset'] = (models.GrantApplication.objects
            .select_related('organization', 'grant_cycle')
            .filter(organization_id=org_pk))

    return super(LogI, self).formfield_for_foreignkey(db_field, request, **kwargs)


class AppCycleI(BaseShowInline):
  """ List related applications on a cycle page """
  model = models.GrantApplication
  readonly_fields = ['organization', 'submission_time', 'pre_screening_status']
  fields = ['organization', 'submission_time', 'pre_screening_status']


class GrantApplicationI(BaseShowInline):
  """ List grant applications on organization page """
  model = models.GrantApplication
  readonly_fields = ('submission_time', 'grant_cycle', 'summary', 'view_or_edit', 'read')
  fields = ('submission_time', 'grant_cycle', 'summary', 'view_or_edit', 'read')

  def queryset(self, request):
    return super(GrantApplicationI, self).queryset(request).select_related('grant_cycle')

  def summary(self, obj):
    """ Display a summary of screening status, giving projects, and awards """

    summary = ''

    if obj.pk:
      summary += obj.get_pre_screening_status_display() + '. '

      projectapps = obj.projectapp_set.all().select_related('giving_project', 'givingprojectgrant')
      for papp in projectapps:
        summary += unicode(papp.giving_project)
        if papp.get_screening_status_display():
          summary += '. ' + papp.get_screening_status_display()
        if hasattr(papp, 'givingprojectgrant'):
          summary += ': ${:,}'.format(int(papp.givingprojectgrant.total_amount()))
        summary += '.\n'

    return summary

  def view_or_edit(self, obj):
    """ Link to grant application change page """
    return ('<a href="/admin/grants/grantapplication/' + str(obj.pk) +
            '/" target="_blank">View details/Edit</a>')
  view_or_edit.allow_tags = True

  def read(self, obj):
    return '<a href="/grants/view/' + str(obj.pk) + '" target="_blank">Read application</a>'
  read.allow_tags = True


class SponsoredProgramI(BaseShowInline):
  """ List sponsored program grants on organization page """
  model = models.SponsoredProgramGrant
  fields = ['amount', 'check_mailed', 'approved', 'edit']
  readonly_fields = fields
  template = 'admin/grants/sponsoredprogramgrant/tabular.html'

  def edit(self, obj):
    if obj.pk:
      return ('<a href="/admin/grants/sponsoredprogramgrant/' + str(obj.pk) +
            '/" target="_blank">View/edit</a>')
    else:
      return ''
  edit.allow_tags = True


class ProjectAppI(admin.TabularInline): # GrantApplication
  """ Display giving projects assigned to this app, and related objects
      (screening status, awards, YER) """
  model = models.ProjectApp
  extra = 1
  fields = ['giving_project', 'screening_status', 'granted', 'year_end_report']
  readonly_fields = ['granted', 'year_end_report']
  verbose_name = 'Giving project'
  verbose_name_plural = 'Giving projects'

  def granted(self, obj):
    """ For existing projectapps, shows grant amount or link to add a grant """
    if obj.pk:
      link = '<a target="_blank" href="/admin/grants/givingprojectgrant/'
      if hasattr(obj, 'givingprojectgrant'):
        award = obj.givingprojectgrant
        link += '{}/">${:,}</a>'
        if obj.givingprojectgrant.grant_length() > 1:
          link += ' (' + str(obj.givingprojectgrant.grant_length()) + '-year)'
        return mark_safe(link.format(award.pk, award.total_amount()))
      else:
        link = link + 'add/?projectapp={}">Enter an award</a>'
        return mark_safe(link.format(obj.pk))
    return ''

  def year_end_report(self, obj):
    if obj.pk:
      reports = (models.YearEndReport.objects.select_related('award')
                                            .filter(award__projectapp_id=obj.pk))
      yer_link = ""
      for i, report in enumerate(reports):
        if i > 0:
          yer_link += " | "
        yer_link += ('<a target="_blank" href="/admin/grants/yearendreport/' +
          str(report.pk) + '/">Year ' + str(i + 1) + '</a>')
      return mark_safe(yer_link)
    return ''

class YERInline(BaseShowInline):
  model = models.YearEndReport
  fields = ['submitted', 'contact_person', 'email', 'phone', 'view']
  readonly_fields = ['submitted', 'contact_person', 'email', 'phone', 'view']

  def view(self, obj):
    return '<a href="/report/view/{}">View</a>'.format(obj.pk)
  view.allow_tags = True

#------------------------------------------------------------------------------
# MODEL ADMIN
#------------------------------------------------------------------------------

class GrantCycleA(admin.ModelAdmin):
  list_display = ['title', 'open', 'close']
  fields = [
    ('title', 'open', 'close'),
    ('info_page', 'email_signature'),
    'private', 'extra_question', 'conflicts',
  ]
  inlines = [AppCycleI]


class OrganizationA(admin.ModelAdmin):
  list_display = ['name', 'email']
  fieldsets = [
    ('', {
      'fields': (('name', 'email'),)
    }),
    ('Staff-entered contact info', {
       'fields': (('staff_contact_person', 'staff_contact_person_title',
                   'staff_contact_phone', 'staff_contact_email'),)
    }),
    ('Contact info from most recent application', {
      'fields':(
        ('address', 'city', 'state', 'zip'),
        ('contact_person', 'contact_person_title', 'telephone_number', 'email_address'),
        ('fax_number', 'website'))
    }),
    ('Organization info from most recent application', {
      'fields': (('founded', 'status', 'ein', 'mission'),)
    }),
    ('Fiscal sponsor info from most recent application', {
      'classes': ('collapse',),
      'fields': (('fiscal_org', 'fiscal_person'),
                ('fiscal_telephone', 'fiscal_address', 'fiscal_email'))
    })
  ]
  search_fields = ['name', 'email']
  inlines = []

  def change_view(self, request, object_id, form_url='', extra_context=None):
    self.inlines = [GrantApplicationI, SponsoredProgramI, LogReadonlyI, LogI]
    self.readonly_fields = [
      'address', 'city', 'state', 'zip', 'telephone_number',
      'fax_number', 'email_address', 'website', 'status', 'ein', 'founded',
      'mission', 'fiscal_org', 'fiscal_person', 'fiscal_telephone',
      'fiscal_address', 'fiscal_email', 'fiscal_letter', 'contact_person',
      'contact_person_title'
    ]
    return super(OrganizationA, self).change_view(request, object_id)


class GrantApplicationA(admin.ModelAdmin):
  list_display = ['organization', 'grant_cycle', 'submission_time', 'read']
  list_filter = ['grant_cycle']
  search_fields = ['organization__name']

  fieldsets = [
    ('Application', {
        'fields': (('organization_link', 'grant_cycle', 'submission_time',
                   'read'),)
    }),
    ('Application contact info', {
        'classes': ('collapse',),
        'description':
            ('Contact information as entered in the grant application. '
              'You may edit this as needed.  Note that the contact information '
              'you see on the organization page is always from the most recent '
              'application, whether that is this or a different one.'),
        'fields': (('address', 'city', 'state', 'zip', 'telephone_number',
                     'fax_number', 'email_address', 'website'),
                   ('status', 'ein'))
    }),
    ('Administration', {
      'fields': (
        ('pre_screening_status', 'scoring_bonus_poc', 'scoring_bonus_geo', 'site_visit_report'),
        ('revert_grant', 'rollover')
      )
    })
  ]
  readonly_fields = ['organization_link', 'grant_cycle', 'submission_time',
                     'read', 'revert_grant', 'rollover']
  inlines = [ProjectAppI, LogReadonlyI, LogI]

  def has_add_permission(self, request):
    return False

  def revert_grant(self, _):
    return '<a href="revert">Revert to draft</a>'
  revert_grant.allow_tags = True

  def rollover(self, _):
    return '<a href="rollover">Copy to another grant cycle</a>'
  rollover.allow_tags = True

  def organization_link(self, obj):
    return (u'<a href="/admin/grants/organization/' + str(obj.organization.pk)
            + '/" target="_blank">' + unicode(obj.organization) + '</a>')
  organization_link.allow_tags = True
  organization_link.short_description = 'Organization'

  def read(self, obj):
    return '<a href="/grants/view/' + str(obj.pk) + '" target="_blank">Read application</a>'
  read.allow_tags = True


class DraftGrantApplicationA(admin.ModelAdmin):
  list_display = ['organization', 'grant_cycle', 'modified', 'overdue',
                  'extended_deadline']
  list_filter = ['grant_cycle']
  fields = [('organization', 'grant_cycle', 'modified'),
            ('extended_deadline')]
  readonly_fields = ['modified']
  form = DraftAdminForm
  search_fields = ['organization__name']

  def get_readonly_fields(self, request, obj=None):
    if obj is not None: # editing - lock org & cycle
      return self.readonly_fields + ['organization', 'grant_cycle']
    return self.readonly_fields


class GivingProjectGrantA(admin.ModelAdmin):
  list_display = ['organization_name', 'grant_cycle', 'giving_project',
                  'short_created', 'total_grant', 'fully_paid', 'check_mailed']
  list_filter = ['agreement_mailed', CycleTypeFilter, GrantCycleYearFilter, MultiYearGrantFilter]
  list_select_related = True

  fieldsets = (
    ('', {
      'fields': (
        ('projectapp', 'total_grant', 'created'),
        ('amount', 'check_number', 'check_mailed'),
        ('agreement_mailed', 'agreement_returned', 'next_year_end_report_due'),
        'approved'
      )
    }),
    ('Multi-Year Grant', {
      'fields': (('second_amount', 'second_check_number', 'second_check_mailed'),)
    })
  )
  readonly_fields = ['created', 'next_year_end_report_due', 'total_grant']

  inlines = [YERInline]

  # ModelAdmin methods (single view)

  def formfield_for_foreignkey(self, db_field, request, **kwargs):
    """ Restrict db query to selected projectapp if specified in url """
    logger.info('gpg page formfield_for_foreignkey')
    if db_field.name == 'projectapp':
      p_app = request.GET.get('projectapp')
      if p_app:
        kwargs['queryset'] = (models.ProjectApp.objects
            .select_related('application', 'application__organization', 'giving_project')
            .filter(pk=p_app))
        logger.info('grant page loaded with projectapp specified ' + p_app)
    return super(GivingProjectGrantA, self).formfield_for_foreignkey(
        db_field, request, **kwargs)

  def get_readonly_fields(self, request, obj=None):
    """ Don't allow projectapp to be changed once the grant has been created """
    if obj is not None:
      self.readonly_fields.append('projectapp')
    return self.readonly_fields

  # custom methods - list and single views

  def next_year_end_report_due(self, obj):
    return obj.yearend_due() or '-'

  def total_grant(self, obj):
    amt = obj.total_amount()
    if amt:
      return '${:,}'.format(amt)
    return '-'

  # custom methods - list page

  def fully_paid(self, obj):
    return obj.fully_paid()
  fully_paid.boolean = True

  def giving_project(self, obj):
    return unicode(obj.projectapp.giving_project)
  giving_project.admin_order_field = 'projectapp__giving_project__title'

  def grant_cycle(self, obj):
    return unicode(obj.projectapp.application.grant_cycle.title)
  grant_cycle.admin_order_field = 'projectapp__application__grant_cycle__title'

  def organization_name(self, obj):
    return obj.projectapp.application.organization.name
  organization_name.admin_order_field = 'projectapp__application__organization__name'

  def short_created(self, obj):
    return obj.created.strftime('%m/%d/%y')
  short_created.short_description = 'Created'
  short_created.admin_order_field = 'created'


class SponsoredProgramGrantA(admin.ModelAdmin):
  list_display = ['organization', 'amount', 'check_mailed']
  list_filter = ['check_mailed']
  exclude = ['entered']
  fields = [('organization', 'amount'),
            ('check_number', 'check_mailed', 'approved'),
            'description']


class YearEndReportA(admin.ModelAdmin):
  list_display = ['org', 'award', 'cycle', 'submitted', 'visible', 'view_link']
  list_filter = ['award__projectapp__application__grant_cycle']
  list_select_related = True
  ordering = ['-submitted']

  fieldsets = [
    ('', {
      'fields': ('award_link', 'submitted', 'view_link')
    }),
    ('', {
      'fields': ('visible',)
    }),
    ('Edit year end report', {
      'classes': ('collapse',),
      'fields': ('email', 'phone', 'website', 'summarize_last_year', 'goal_progress',
        'quantitative_measures', 'evaluation', 'achieved', 'collaboration', 'new_funding',
        'major_changes', 'total_size', 'donations_count', 'donations_count_prev')
    })
  ]
  readonly_fields = ['award', 'award_link', 'submitted', 'view_link']

  def view_link(self, obj):
    if obj.pk:
      url = reverse('sjfnw.grants.views.view_yer', kwargs={'report_id': obj.pk})
      return '<a href="%s" target="_blank">View report</a>' % url
  view_link.allow_tags = True
  view_link.short_description = 'View'

  def award_link(self, obj):
    if obj.pk:
      url = reverse('admin:grants_givingprojectgrant_change', args=(obj.pk,))
      return '<a target="_blank" href="{}">{}</a>'.format(url, obj.award.full_description())
  award_link.allow_tags = True
  award_link.short_description = 'Award'


  def org(self, obj):
    return obj.award.projectapp.application.organization.name
  org.admin_order_field = 'award__projectapp__application__organization'

  def cycle(self, obj):
    return obj.award.projectapp.application.grant_cycle
  cycle.admin_order_field = 'award__projectapp__application__grant_cycle'

class DraftAdv(admin.ModelAdmin):
  """ Only used in admin-advanced """
  list_display = ['organization', 'grant_cycle', 'modified', 'overdue',
                  'extended_deadline']
  list_filter = ['grant_cycle']


# REGISTER

admin.site.register(models.GrantCycle, GrantCycleA)
admin.site.register(models.Organization, OrganizationA)
admin.site.register(models.GrantApplication, GrantApplicationA)
admin.site.register(models.DraftGrantApplication, DraftGrantApplicationA)
admin.site.register(models.GivingProjectGrant, GivingProjectGrantA)
admin.site.register(models.SponsoredProgramGrant, SponsoredProgramGrantA)
admin.site.register(models.YearEndReport, YearEndReportA)

advanced_admin.register(models.GrantCycle, GrantCycleA)
advanced_admin.register(models.Organization, OrganizationA)
advanced_admin.register(models.GrantApplication, GrantApplicationA)
advanced_admin.register(models.DraftGrantApplication, DraftAdv)
advanced_admin.register(models.GivingProjectGrant, GivingProjectGrantA)
advanced_admin.register(models.SponsoredProgramGrant, SponsoredProgramGrantA)
