import logging
logger = logging.getLogger('sjfnw')

def create_link(url, text, new_tab=False):
  new_tab = ' target="_blank"' if new_tab else ''
  return '<a href="{}"{}>{}</a>'.format(url, new_tab, text)
