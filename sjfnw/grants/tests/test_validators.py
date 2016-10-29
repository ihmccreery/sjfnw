# encoding: utf-8

import re

from django.core.exceptions import ValidationError
from django.test import TestCase

from sjfnw.grants.models import WordLimitValidator

def simple_clean(val):
  """ Clean method used as of 9d8b1d9 (tag 2016-08-03)
      Included here to ensure that count from new method is always lte old
  """
  return len(re.findall(r'[^ \n\r]+', val))

# "simple" indicates whether the simple_clean method should give an accurate word count
EXAMPLES = [
  {
    'text': ('Please fill in this timeline to describe your activities over the'
      ' next five quarters. This will not exactly match up with the time period'
      ' funded by this grant.\nWe are asking for this information to give us an idea'
      ' of what-your work looks like: what you are doing and how those activities'
      ' intersect and build on each other and move you towards your goals. Because'
      ' our grants are usually general operating funds, we want to get a sense of'
      ' what your organizing work looks like over time.\rNote: We understand that'
      ' this timeline is based only on what you know r\'now and that'
      ' circumstances change.\r\n'),
    'expected_count': 105,
    'simple': True
  },
  {
    'text': (u'This gránt will provide funding for two years. While we know it'
      u' can be difficult to predict your work beyond a year, please give us an'
      u' idea of what the second year might look like.\t - • What overall goals and'
      u' strategies ø∆cat do you – forecast in the second year?\t* How will the second year'
      u' of this grant éñôcat build on your work in the first year?\r'),
    'expected_count': 65,
    'simple': False
  }
]


class WordLimit(TestCase):

  def test_compare(self):
    """ Should return true if first arg is gt second, else false """
    validator = WordLimitValidator(limit_value=15)
    self.assertFalse(validator.compare(1, 2))
    self.assertTrue(validator.compare(9, 3))
    self.assertFalse(validator.compare(0, 0))

  def test_clean(self):
    validator = WordLimitValidator(limit_value=5)
    for example in EXAMPLES:
      word_count = validator.clean(example['text'])
      prior_word_count = simple_clean(example['text'])

      self.assertEqual(word_count, example['expected_count'])

      if example['simple']:
        self.assertEqual(word_count, prior_word_count)
      else:
        self.assertLess(word_count, prior_word_count)

  def test_call_exception(self):
    """ Should raise exception when word count is over limit """
    validator = WordLimitValidator(limit_value=5)

    validator('* a - b - c,') # should not raise exception

    self.assertRaisesRegexp(
        ValidationError,
        "[u'This field has a maximum word count of 5 (current count: 7)']",
        validator, 'a b ced   sers  a as\nio')
