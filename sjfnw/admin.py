from django.contrib import admin, messages
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

import logging
logger = logging.getLogger('sjfnw')

# Configure admin site
#----------------------

admin.site.index_template = 'admin/index_custom.html'
admin.site.site_header = 'Social Justice Fund Apps'
admin.site.site_title = 'SJF Apps'

# SHARED

class YearFilter(admin.SimpleListFilter):
  """ Base filter by year. Usage: create a child class and override the class variables:

    Required override:
      filter_model: the model that has the date field to use for filtering

    Optional overrides:
      intermediate: string that connects the model being filtered to the filter_model
                    (required if the model being filtered != the filter_model)
      title: displayed in filters sidebar (default: 'year')
      parameter_name: query parameter name (default: 'year')
  """
  title = 'year'
  parameter_name = 'year'
  filter_model = None
  field = ''
  intermediate = ''

  def lookups(self, request, model_admin):
    dates = (self.filter_model.objects
        .values_list(self.field, flat=True)
        .order_by('-%s' % self.field))
    prev = None
    years = []
    for date in dates:
      if date.year != prev:
        years.append((date.year, date.year))
        prev = date.year
    return years

  def queryset(self, request, queryset):
    val = self.value()
    if not val:
      return queryset
    try:
      year = int(val)
    except ValueError:
      logger.error('YearFilter received invalid value %s', val)
      messages.error(request,
          'Error loading filter. Contact techsupport@socialjusticefund.org')
      return queryset
    else:
      filt = {}
      key = self.intermediate + '__' if self.intermediate else ''
      filt['{}{}__year'.format(key, self.field)] = year
      return queryset.filter(**filt)



# REGISTER

advanced_admin = AdminSite(name='advanced')

admin.site.unregister(Group)

advanced_admin.register(User, UserAdmin)
advanced_admin.register(Group)
advanced_admin.register(Permission)
advanced_admin.register(ContentType)
