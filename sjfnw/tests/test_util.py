from django.test import TestCase

from sjfnw import utils

class CreateLink(TestCase):

  url = 'http://google.com'
  text = 'Search'

  def test_simple(self):
    link = utils.create_link(self.url, self.text)
    self.assertEqual(link, '<a href="{}">{}</a>'.format(self.url, self.text))

  def test_new_window(self):
    link = utils.create_link(self.url, self.text, new_tab=True)
    self.assertEqual(link, '<a href="{}" target="_blank">{}</a>'.format(self.url, self.text))
