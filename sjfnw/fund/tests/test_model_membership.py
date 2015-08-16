from django.utils import timezone

from sjfnw.fund.models import Membership, Donor, Step
from sjfnw.fund.tests.base import BaseFundTestCase

class UpdateStory(BaseFundTestCase):

  def setUp(self):
    super(UpdateStory, self).setUp()
    self.create_test()
    self.membership = Membership.objects.get(pk=self.ship_id)
    # assert that each test starts without an existing news story
    story_count = self.membership.newsitem_set.count()
    self.assertEqual(story_count, 0)

  def test_nothing(self):
    self.membership.update_story(timezone.now())
    story_count = self.membership.newsitem_set.count()
    self.assertEqual(story_count, 0)

  def test_talk(self):
    now = timezone.now()
    step = Step(donor_id=self.donor_id, date=now, description='Talk to this person')
    step.completed = now
    step.save()

    self.membership.update_story(timezone.now())

    stories = self.membership.newsitem_set.all()
    self.assertEqual(len(stories), 1)
    story = stories[0]
    self.assertEqual(story.summary, u'Test talked to 1 person.')

  def test_ask(self):
    now = timezone.now()
    step = Step(donor_id=self.donor_id, date=now, description='Talk to this person')
    step.completed = now
    step.asked = True
    step.save()

    self.membership.update_story(timezone.now())

    stories = self.membership.newsitem_set.all()
    self.assertEqual(len(stories), 1)
    story = stories[0]
    self.assertEqual(story.summary, u'Test asked 1 person.')

  def test_ask_with_promise(self):
    now = timezone.now()
    step = Step(donor_id=self.donor_id, date=now, description='Talk to this person')
    step.completed = now
    step.asked = True
    step.promised = 50
    step.save()

    self.membership.update_story(timezone.now())

    stories = self.membership.newsitem_set.all()
    self.assertEqual(len(stories), 1)
    story = stories[0]
    self.assertEqual(story.summary, u'Test asked 1 person and got $50 in promises.')

  def test_talk_with_promise(self):
    now = timezone.now()
    step = Step(donor_id=self.donor_id, date=now, description='Talk to this person')
    step.completed = now
    step.promised = 50
    step.save()

    self.membership.update_story(timezone.now())

    stories = self.membership.newsitem_set.all()
    self.assertEqual(len(stories), 1)
    story = stories[0]
    self.assertEqual(story.summary, u'Test talked to 1 person and got $50 in promises.')

  def test_multiple_same_donor(self):
    now = timezone.now()
    step = Step(donor_id=self.donor_id, date=now, description='Talk to this person')
    step.completed = now
    step.save()

    step = Step(donor_id=self.donor_id, date=now, description='Follow up')
    step.completed = now
    step.save()

    self.membership.update_story(timezone.now())

    stories = self.membership.newsitem_set.all()
    self.assertEqual(len(stories), 1)
    story = stories[0]
    self.assertEqual(story.summary, u'Test talked to 1 person.')

  def test_combo(self):
    now = timezone.now()
    step = Step(donor_id=self.donor_id, date=now, description='Talk to this person')
    step.completed = now
    step.save()

    step = Step(donor_id=self.donor_id, date=now, description='Follow up')
    step.completed = now
    step.save()

    donor2 = Donor(membership_id=self.membership.pk, firstname='ADA')
    donor2.save()

    step = Step(donor_id=donor2.pk, date=now, description='Ask this other person')
    step.completed = now
    step.asked = True
    step.promised = 150
    step.save()

    donor3 = Donor(membership_id=self.membership.pk, firstname='Uncle so and so')
    donor3.save()

    step = Step(donor_id=donor3.pk, date=now, description='Ask for $$$')
    step.completed = now
    step.promised = 500
    step.save()

    self.membership.update_story(timezone.now())

    stories = self.membership.newsitem_set.all()
    self.assertEqual(len(stories), 1)
    story = stories[0]
    self.assertEqual(story.summary,
        u'Test talked to 2 people, asked 1 and got $650 in promises.')
