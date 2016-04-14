import logging

from django import http
from django.shortcuts import render

logger = logging.getLogger('sjfnw')

def _get_context(path):
  if path.find('/fund') == 0:
    title_addition = ' - Project Central'
    contact_url = '/fund/support'
  elif path.find('/org') == 0 or path.find('/apply') == 0:
    title_addition = ' - Social Justice Fund Grants'
    contact_url = '/org/support'
  else:
    title_addition = ' - Social Justice Fund Apps'
    contact_url = ''

  return {
    'title_addition': title_addition,
    'contact_url': contact_url
  }

def page_not_found(request):
  """ Modified version of default handler. Renders app-specific template. """
  page_context = _get_context(request.path)
  return http.HttpResponseNotFound(render(request, '404.html', page_context))

def server_error(request):
  """ Modified version of default handler. Renders app-specific template. """
  page_context = _get_context(request.path)
  return http.HttpResponseNotFound(render(request, '500.html', page_context))

def log_javascript(request):
  """ Receives javascript errors and logs them """
  if request.method == 'POST':
    log = ''
    for key in request.POST:
      log = log + '\n' + key + ': ' + str(request.POST[key])
    logger.warning(log)
  return http.HttpResponse('success')
