from django.test import TestCase
from django.utils import timezone

from sjfnw.fund.models import GivingProject, Member, Membership

class ModelUnicodes(TestCase):

  def test_unicode(self):
    project = GivingProject(title='A Fake Giving Project',
        fundraising_training=timezone.now(),
        fundraising_deadline=timezone.now()
      )
    project.save()
    member = Member(first_name='Al', last_name='Fisher')
    member.save()
    membership = Membership(giving_project=project, member=member)
    self.assertEqual(u'Al Fisher', unicode(member))
    self.assertEqual(u'A Fake Giving Project %d' % timezone.now().year, unicode(project))
    self.assertEqual(u'Al Fisher, A Fake Giving Project %d' % timezone.now().year, unicode(membership))

