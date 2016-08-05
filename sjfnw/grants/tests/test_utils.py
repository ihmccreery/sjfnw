# encoding: utf-8

from django.test import TestCase

from sjfnw.grants import utils

class StripPuncuation(TestCase):

  def test_str(self):
    result = utils.strip_punctuation('Hello, here\'s a list : - one! * two; + three')
    self.assertEqual(result, 'Hello heres a list   one  two  three')

    result = utils.strip_punctuation('Watch=these, / ^other $chars@get (removed) `too\r &&')
    self.assertEqual(result, 'Watchthese  other charsget removed too\r ')

  def test_unicode(self):
    result = utils.strip_punctuation(u'Hello‚ here’s å lˆst – □ oñe▶ ● two; +◇ thrée')
    self.assertEqual(result, u'Hello heres å lst   oñe  two  thrée')

    result = utils.strip_punctuation(u'Watch‐these, • ‘other ▹chars‒get “removed” `too\r ■')
    self.assertEqual(result, u'Watchthese  other charsget removed too\r ')
