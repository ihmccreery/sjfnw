import logging
import sys
import time

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.runner import DiscoverRunner

from unittest import TextTestRunner, TestResult
from unittest.signals import registerResult

# Sets root & sjfnw loggers level. Comment out for less output.
logging.getLogger().setLevel(0)
logger = logging.getLogger('sjfnw')
logger.setLevel(0)

RED = '\033[00;31m'
GREEN = '\033[00;32m'
YELLOW = '\033[00;33m'
BOLD = '\033[1m'
BOLD_RED = '\033[01;31m'
RESET = '\033[00m'
INDENT = '    '

class BaseTestCase(TestCase):
  """ Base test case used by all other tests

    Provides login methods and custom assertion(s) """

  def log_in_testy(self):
    User.objects.create_user('testacct@gmail.com', 'testacct@gmail.com', 'testy')
    self.client.login(username='testacct@gmail.com', password='testy')

  def log_in_newbie(self):
    User.objects.create_user('newacct@gmail.com', 'newacct@gmail.com', 'noob')
    self.client.login(username='newacct@gmail.com', password='noob')

  def log_in_admin(self): #just a django superuser
    User.objects.create_superuser('admin@gmail.com', 'admin@gmail.com', 'admin')
    self.client.login(username='admin@gmail.com', password='admin')

  def assert_message(self, response, text):
    """ Asserts that a message (django.contrib.messages) with the given text
        is displayed """
    messages = list(response.context['messages'])
    self.assertEqual(1, len(messages))
    self.assertEqual(str(messages[0]), text)

  class Meta: # pylint: disable=old-style-class
    abstract = True


# Code below overrides the default test runner to provide colored
# output in the console

# pylint: disable=too-many-arguments,too-many-branches,too-many-locals,
# pylint: disable=redefined-builtin,invalid-name,bad-builtin

class ColorTestSuiteRunner(DiscoverRunner):
  """ Redirects run_suite to ColorTestRunner """

  def run_suite(self, suite, **kwargs):
    return ColorTestRunner(verbosity=2, failfast=self.failfast).run(suite)


class ColorTextResult(TestResult):
  """Copied and modified from py2.7's TextTestResult

    A test result class that can print formatted text results to a stream.
  """

  separator1 = '=' * 70
  separator2 = '-' * 70

  def __init__(self, stream, descriptions, verbosity):
    super(ColorTextResult, self).__init__(stream, descriptions, verbosity)
    self.stream = stream
    self.show_all = verbosity > 1
    self.dots = verbosity == 1
    self.descriptions = descriptions

  def get_description(self, test):
    """ modified to bold test name and strip repeat parts (sjfnw, test_) """
    doc_first_line = test.shortDescription()
    # test.id() is in format module.filename.testclass.testmethod. example:
    # sjfnw.fund.tests.test_add_mult.AddMultipleDonorsPost.test_post_empty
    name = test.id().replace('sjfnw.', '').replace('tests.', '').replace('.test_', '  ')
    if self.descriptions and doc_first_line:
      return '\n{}{}{} {}'.format(BOLD, name, RESET, doc_first_line)
    else:
      return '\n{}{}{}\n'.format(BOLD, name, RESET)

  def startTest(self, test):
    super(ColorTextResult, self).startTest(test)
    if self.show_all:
      self.stream.writeln(self.get_description(test))

  def addSuccess(self, test):
    super(ColorTextResult, self).addSuccess(test)
    if self.show_all:
      self.stream.writeln(INDENT + GREEN + 'ok' + RESET)
    elif self.dots:
      self.stream.write('.')
      self.stream.flush()

  def addError(self, test, err):
    super(ColorTextResult, self).addError(test, err)
    if self.show_all:
      self.stream.writeln(INDENT + RED + 'ERROR' + RESET)
    elif self.dots:
      self.stream.write('E')
      self.stream.flush()

  def addFailure(self, test, err):
    super(ColorTextResult, self).addFailure(test, err)
    if self.show_all:
      self.stream.writeln(INDENT + RED + 'FAIL' + RESET)
    elif self.dots:
      self.stream.write('F')
      self.stream.flush()

  def addSkip(self, test, reason):
    super(ColorTextResult, self).addSkip(test, reason)
    if self.show_all:
      self.stream.writeln('{}{}skipped{} {!r}'.format(INDENT, YELLOW, RESET, reason))
    elif self.dots:
      self.stream.write('s')
      self.stream.flush()

  def addExpectedFailure(self, test, err):
    super(ColorTextResult, self).addExpectedFailure(test, err)
    if self.show_all:
      self.stream.writeln(INDENT + GREEN + 'expected failure' + RESET)
    elif self.dots:
      self.stream.write('x')
      self.stream.flush()

  def addUnexpectedSuccess(self, test):
    super(ColorTextResult, self).addUnexpectedSuccess(test)
    if self.show_all:
      self.stream.writeln(INDENT + RED + 'unexpected success' + RESET)
    elif self.dots:
      self.stream.write('u')
      self.stream.flush()

  def printErrors(self):
    if self.dots or self.show_all:
      self.stream.writeln()
    self.print_error_list('ERROR', self.errors)
    self.print_error_list('FAIL', self.failures)

  def print_error_list(self, flavour, errors):
    for test, err in errors:
      self.stream.writeln(self.separator1)
      self.stream.writeln('{}{}{}: {}{}{}'.format(BOLD_RED, flavour, RESET, RED, test, RESET))
      self.stream.writeln(self.separator2)
      self.stream.writeln(err)


class ColorTestRunner(TextTestRunner):
  """ Colorizes the summary results at the end
  Uses ColorTextResult instead of TextTestResult """

  def __init__(self, stream=sys.stderr, descriptions=True, verbosity=2,
               failfast=False, buffer=False, resultclass=None):
    super(ColorTestRunner, self).__init__(stream, descriptions, verbosity,
                                          failfast, buffer, resultclass)
    self.resultclass = ColorTextResult

  def run(self, test):
    """ Copied and modified from TextTestRunner

      Run the given test case or test suite."""

    result = self._makeResult()
    registerResult(result)
    result.failfast = self.failfast
    result.buffer = self.buffer
    start_time = time.time()
    startTestRun = getattr(result, 'startTestRun', None)
    if startTestRun is not None:
      startTestRun()
    try:
      test(result)
    finally:
      stopTestRun = getattr(result, 'stopTestRun', None)
      if stopTestRun is not None:
        stopTestRun()
    stop_time = time.time()
    timeTaken = stop_time - start_time
    result.printErrors()
    if hasattr(result, 'separator2'):
      self.stream.writeln(result.separator1)
    run = result.testsRun
    self.stream.writeln(' \033[1mRan %d test%s in %.3fs' %
        (run, run != 1 and 's' or '', timeTaken))
    self.stream.writeln()

    expectedFails = unexpectedSuccesses = skipped = 0
    try:
      results = map(len, (result.expectedFailures,
        result.unexpectedSuccesses,
        result.skipped))
    except AttributeError:
      pass
    else:
      expectedFails, unexpectedSuccesses, skipped = results

    infos = []
    if not result.wasSuccessful():
      self.stream.write(' \033[1;31mFAILED\033[00m')
      failed, errored = map(len, (result.failures, result.errors))
      if failed:
        infos.append('failures = \033[00;31m%d\033[00m' % failed)
      if errored:
        infos.append('errors = \033[00;31m%d\033[00m' % errored)
    else:
      self.stream.write(' \033[1;32mOK\033[00m')
    if skipped:
      infos.append('skipped = \033[00;33m%d\033[00m' % skipped)
    if expectedFails:
      infos.append('expected failures=%d' % expectedFails)
    if unexpectedSuccesses:
      infos.append('unexpected successes=%d' % unexpectedSuccesses)
    if infos:
      self.stream.writeln(' (%s)' % (', '.join(infos),))
    self.stream.write('\n')
    return result