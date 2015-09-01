from django.conf.urls import patterns, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import RedirectView, TemplateView

from sjfnw.admin import advanced_admin
from sjfnw.grants.urls import apply_urls, report_urls, grants_urls, root_urls

# pylint: disable=invalid-name

handler404 = 'sjfnw.views.page_not_found'
handler500 = 'sjfnw.views.server_error'

admin.autodiscover() # load admin.py from all apps

"""
if settings.DEBUG:
  import debug_toolbar
  urlpatterns += patterns('',
    url(r'^__debug__/', include(debug_toolbar.urls)),
  )
"""

urlpatterns = patterns('',
  (r'^/?$', TemplateView.as_view(template_name='home.html')),

  # project central
  (r'^fund$', 'sjfnw.fund.views.home'),
  (r'^fund/', include('sjfnw.fund.urls')),
  (r'^fund/logout/?$', 'django.contrib.auth.views.logout', {'next_page': '/fund'}),

  # grants
  (r'^apply$', 'sjfnw.grants.views.org_home'),
  (r'^apply/', include(apply_urls)),
  (r'^grants/', include(grants_urls)),
  (r'^report/', include(report_urls)),
  (r'^', include(root_urls)),
  (r'^org/?$', 'sjfnw.grants.views.redirect_to_apply'),
  (r'^logout/?$', 'django.contrib.auth.views.logout', {'next_page': '/apply'}),
  (r'^get-upload-url/?', 'sjfnw.grants.views.RefreshUploadUrl'), #TODO put this under /apply

  # admin
  (r'^admin/', include(admin.site.urls)),
  (r'^admin-advanced/', include(advanced_admin.urls)),
  (r'^admin$', RedirectView.as_view(url='/admin/')),
  (r'^admin-advanced$', RedirectView.as_view(url='/admin-advanced/')),
  (r'^admin/grants/grantapplication/(?P<app_id>\d+)/revert', 'sjfnw.grants.views.AppToDraft'),
  (r'^admin-advanced/grants/grantapplication/(?P<app_id>\d+)/revert',
      'sjfnw.grants.views.AppToDraft'),
  (r'^admin/grants/grantapplication/(?P<app_id>\d+)/rollover',
      'sjfnw.grants.views.AdminRollover'),
  (r'^admin-advanced/grants/grantapplication/(?P<app_id>\d+)/rollover',
      'sjfnw.grants.views.AdminRollover'),
  (r'^admin/grants/organization/login', 'sjfnw.grants.views.Impersonate'),
  (r'^admin/grants/organization/(?P<org_id>\d+)/update', 'sjfnw.grants.views.update_profile'),
  (r'^admin/grants/givingprojectgrant/yer-status', 'sjfnw.grants.views.show_yer_statuses'),

  #reporting
  (r'^admin/grants/search/?', 'sjfnw.grants.views.grants_report'),

  # cron emails
  (r'^mail/overdue-step', 'sjfnw.fund.cron.email_overdue'),
  (r'^mail/new-accounts', 'sjfnw.fund.cron.new_accounts'),
  (r'^mail/gifts', 'sjfnw.fund.cron.gift_notify'),
  (r'^mail/drafts/?', 'sjfnw.grants.views.DraftWarning'),
  (r'^mail/yer/?', 'sjfnw.grants.views.yer_reminder_email'),

  # dev
  (r'^dev/jslog/?', 'sjfnw.views.log_javascript')
)

#for dev_appserver
urlpatterns += staticfiles_urlpatterns()
