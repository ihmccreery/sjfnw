from django.core.exceptions import ValidationError
from django.test import TestCase

from sjfnw.grants.models import WordLimitValidator

class WordLimit(TestCase):

  def test_compare(self):
    """ Should return true if first arg is gt second, else false """
    validator = WordLimitValidator(limit_value=15)
    self.assertFalse(validator.compare(1, 2))
    self.assertTrue(validator.compare(9, 3))
    self.assertFalse(validator.compare(0, 0))

  def test_clean_simple(self):
    """ Should return word count """
    validator = WordLimitValidator(limit_value=5)
    self.assertEqual(validator.clean('a b c def'), 4)
    self.assertEqual(validator.clean('a ba-lw c\ndef a\r  "e, r" u badsads askdk j j '), 12)

  def test_call(self):
    """ Should raise exception when word count is over limit """
    validator = WordLimitValidator(limit_value=5)

    validator('a b c')

    self.assertRaisesRegexp(
        ValidationError,
        "[u'This field has a maximum word count of 5 (current count: 7)']",
        validator, 'a b ced   sers  a as\nio')
