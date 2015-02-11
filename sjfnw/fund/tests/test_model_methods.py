from sjfnw.fund.models import GivingProject
from sjfnw.fund.tests.base import BaseFundTestCase, TEST_FIXTURE

class GetSuggestedSteps(BaseFundTestCase):

  def setUp(self):
    super(GetSuggestedSteps, self).setUp()
    self.gp = GivingProject.objects.get(title='Pre training')

  def test_empty(self):
    self.gp.suggested_steps = ''
    self.gp.save()
    suggested = self.gp.get_suggested_steps()
    self.assertEqual(suggested, [])

  def test_basic(self):
    self.gp.suggested_steps = 'Talk to person\r\nInvite them to a thing\nThanks!!'
    self.gp.save()
    suggested = self.gp.get_suggested_steps()
    self.assertEqual(len(suggested), 3)
    self.assertEqual(suggested[0], 'Talk to person')
    self.assertEqual(suggested[1], 'Invite them to a thing')
    self.assertEqual(suggested[2], 'Thanks!!')

  def test_empty_lines(self):
    self.gp.suggested_steps = 'Talk to person\r\nInvite them to a thing\n\n\nThanks!!\r\n'
    self.gp.save()
    suggested = self.gp.get_suggested_steps()
    self.assertEqual(len(suggested), 3)
    self.assertEqual(suggested[0], 'Talk to person')
    self.assertEqual(suggested[1], 'Invite them to a thing')
    self.assertEqual(suggested[2], 'Thanks!!')

  def test_whitespace(self):
    self.gp.suggested_steps = 'Talk to person     \r\n   Invite them to a thing\n  \n\nThanks!!\r\n   '
    self.gp.save()
    suggested = self.gp.get_suggested_steps()
    self.assertEqual(len(suggested), 3)
    self.assertEqual(suggested[0], 'Talk to person')
    self.assertEqual(suggested[1], 'Invite them to a thing')
    self.assertEqual(suggested[2], 'Thanks!!')


