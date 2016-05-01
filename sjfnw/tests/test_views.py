from sjfnw.tests.base import BaseTestCase

class TopLevelViews(BaseTestCase):

  def setUp(self):
    super(TopLevelViews, self).setUp()

  def test_page_not_found(self):
    res = self.client.get('/unknown')
    self.assertTemplateUsed(res, '404.html')
