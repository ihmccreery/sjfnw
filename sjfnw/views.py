from django import http
from django.shortcuts import render
import logging

logger = logging.getLogger('sjfnw')

# 404
def page_not_found(request):
  """ Modified version of default handler which returns app-specific template. """
  path = request.path
  if path.find('/fund') == 0:
    title_addition = ' - Project Central'
    contact_url = '/fund/support'
  elif path.find('/org') == 0 or  path.find('/apply') == 0:
    title_addition = ' - Social Justice Fund Grants'
    contact_url = '/org/support'
  else:
    title_addition = ' - Social Justice Fund Apps'
    contact_url = False
  return http.HttpResponseNotFound(render(request, '404.html', {
    'title_addition': title_addition, 'contact_url':contact_url
  }))

# 500
def server_error(request):
  """ Modified version of default handler which returns app-specific template. """
  path = request.path
  if path.find('/fund') == 0:
    title_addition = ' - Project Central'
    contact_url = '/fund/support'
  elif path.find('/org') == 0 or  path.find('/apply') == 0:
    title_addition = ' - Social Justice Fund Grants'
    contact_url = '/org/support'
  else:
    title_addition = ' - Social Justice Fund Apps'
    contact_url = False
  return http.HttpResponseNotFound(render(request, '500.html', {
    'title_addition': title_addition, 'contact_url':contact_url
  }))

# endpoint for logging javascript errors to server log
def log_javascript(request):
  if request.method == 'POST':
    log = ''
    for key in request.POST:
      log = log + '\n' + key + ': ' + str(request.POST[key])
    logger.warning(log)
  return http.HttpResponse('success')
