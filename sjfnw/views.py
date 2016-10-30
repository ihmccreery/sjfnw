import logging

from django import http
from django.conf import settings
from django.shortcuts import render

from sjfnw import constants as c

logger = logging.getLogger('sjfnw')

def _get_context(path):

  if path.startswith('/fund'):
    base_template = 'fund/_base.html'
    title_addition = ' - Project Central'
    contact_url = '/fund/support'

  elif path.startswith('/apply') or path.startswith('/org'):
    base_template = 'grants/base.html'
    title_addition = ' - Social Justice Fund Grants'
    contact_url = '/org/support'

  else:
    base_template = 'base.html'
    title_addition = ' - Social Justice Fund Apps'
    contact_url = ''

  return {
    'base_template': base_template,
    'title_addition': title_addition,
    'contact_url': contact_url
  }

def page_not_found(request):
  """ Custom 404 handler. Renders template with app-specific context. """
  page_context = _get_context(request.path)
  return http.HttpResponseNotFound(render(request, '404.html', page_context))

def server_error(request):
  """ Custom 500 handler. Renders template with app-specific context. """
  page_context = _get_context(request.path)
  return http.HttpResponseServerError(render(request, '500.html', page_context))

def maintenance(request):
  """ Page displayed if site is down for maintenance """
  page_context = {
    'maintenance_end': settings.MAINTENANCE_END_DISPLAY,
    'support_email': c.SUPPORT_EMAIL
  }
  return render(request, 'maintenance.html', page_context, status=503)

def log_javascript(request):
  """ Receives javascript errors and logs them """
  if request.method == 'POST':
    log = ''
    for key in request.POST:
      log = log + '\n' + key + ': ' + str(request.POST[key])
    logger.warning(log)
  return http.HttpResponse('success')
