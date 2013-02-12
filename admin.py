﻿from django.conf import settings
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from fund.models import *
from grants.models import *
import fund.forms, fund.utils
import logging

## FUND

""" signals needed:
  user save - if is_staff, add to group?
  gp save - remove blank lines in s_steps
  """

def approve(modeladmin, request, queryset):
  logging.info('Approval button pressed; looking through queryset')
  for memship in queryset:
    if memship.approved == False:
      fund.utils.NotifyApproval(memship)  
  queryset.update(approved=True)
  logging.info('Approval queryset updated')    

def overdue_steps(obj):
  return obj.has_overdue()

def estimated(obj):
  return obj.estimated()
  
def pledged(obj):
  return obj.pledged()

class MembershipAdmin(admin.ModelAdmin):
  list_display = ('member', 'giving_project', estimated, pledged, overdue_steps, 'last_activity', 'approved', 'leader')
  actions = [approve]
  list_filter = ('approved', 'leader', 'giving_project') #add overdue steps

class MembershipInline(admin.TabularInline):
  model = Membership
  formset = fund.forms.MembershipInlineFormset
  extra = 0
  can_delete = False
  fields = ('member', 'approved', 'leader',)

class ProjectResourcesInline(admin.TabularInline):
  model = ProjectResource
  extra = 0
  template = 'admin/fund/tabular_projectresource.html'
  fieldsets = (None, {
    'classes': ('collapse',),
    'fields': ('resource', 'session',)
  }),

def gp_year(obj):
  return obj.fundraising_deadline.year
gp_year.short_description = 'Year'

class GPAdmin(admin.ModelAdmin):
  list_display = ('title', gp_year)
  fields = (
    ('title', 'public'),
    ('fundraising_training', 'fundraising_deadline'),
    'fund_goal',
    'calendar',
    'suggested_steps',
    'pre_approved',
   )
  inlines = [
    ProjectResourcesInline,
    MembershipInline,
  ]
  
class DonorAdmin(admin.ModelAdmin):
  list_display = ('firstname', 'lastname', 'membership', 'amount', 'pledged', 'gifted')
  list_filter = ('membership__giving_project', 'asked')
  list_editable = ('gifted',)
  search_fields = ['firstname', 'lastname']

class NewsAdmin(admin.ModelAdmin):
  list_display = ('summary', 'date', 'membership')
  list_filter = ('membership__giving_project',)

#advanced only
class MemberAdvanced(admin.ModelAdmin):
  list_display = ('__unicode__', 'email')
  search_fields = ['first_name', 'last_name', 'email']
  def get_model_perms(self, request):
    #Return empty perms dict thus hiding the model from admin index.
    return {}

def step_membership(obj):
  return obj.donor.membership

class StepAdv(admin.ModelAdmin):
  list_display = ('description', 'donor', step_membership, 'date', 'completed')

## GRANTS

class GrantAppAdmin(admin.ModelAdmin):
  fields = ('screening_status', 'grant_cycle', 'scoring_bonus_poc', 'scoring_bonus_geo')
  list_display = ('organization', 'submission_time', 'screening_status')  

class DraftAdmin(admin.ModelAdmin):
  list_display = ('organization', 'grant_cycle', 'modified')
  readonly_fields = ('fiscal_letter', 'budget', 'demographics', 'funding_sources')

def view_grant_link(obj):
  return '<a href="/grants/view/' + str(obj.pk) + '/">' + str(obj.submission_time) + '</a>'
  
class GrantAppInline(admin.TabularInline):
  model = GrantApplication
  extra = 0
  max_num = 0
  can_delete = False
  readonly_fields = ('submission_time', 'grant_cycle', 'screening_status')
  fieldsets = (
    ('fuck this?', {
      'fields': ('submission_time', 'grant_cycle', 'screening_status')
    }),
  )

class OrganizationAdmin(admin.ModelAdmin):
  list_display = ('name', 'email',)
  fields = (
    ('name', 'email', 'telephone_number'),
    ('address', 'city', 'state', 'zip'),
    ('fiscal_letter'),
  )
  readonly_fields = ('address', 'city', 'state', 'zip', 'telephone_number', 'fax_number', 'email_address', 'website', 'status', 'ein', 'fiscal_letter')
  inlines = (GrantAppInline,)

## ADMIN SITES

#default
admin.site.unregister(User) # have to make contrib/auth/admin.py load first..
admin.site.unregister(Group)
admin.site.register(Member, MemberAdvanced)
admin.site.register(GivingProject, GPAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(NewsItem, NewsAdmin)
admin.site.register(Donor, DonorAdmin)
admin.site.register(Resource)

#advanced
advanced_admin = AdminSite(name='advanced')

advanced_admin.register(User, UserAdmin)
advanced_admin.register(Group)
advanced_admin.register(Permission)
advanced_admin.register(ContentType)

advanced_admin.register(Member, MemberAdvanced)
advanced_admin.register(Donor, DonorAdmin)
advanced_admin.register(Membership, MembershipAdmin)
advanced_admin.register(GivingProject, GPAdmin)
advanced_admin.register(NewsItem, NewsAdmin)
advanced_admin.register(Step, StepAdv)
advanced_admin.register(ProjectResource)
advanced_admin.register(Resource)

advanced_admin.register(GrantCycle)
advanced_admin.register(Organization, OrganizationAdmin)
advanced_admin.register(GrantApplication, GrantAppAdmin)
advanced_admin.register(DraftGrantApplication, DraftAdmin)