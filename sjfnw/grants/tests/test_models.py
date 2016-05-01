from django.test import TestCase

from sjfnw.grants.models import Organization

class OrganizationGetStaffEntered(TestCase):

  def test_none(self):
    org = Organization()
    self.assertEqual(org.get_staff_entered_contact_info(), '')

  def test_some(self):
    org = Organization(staff_contact_person_title='Mx', staff_contact_email='who@what.z')
    self.assertEqual(org.get_staff_entered_contact_info(), 'Mx, who@what.z')

  def test_all(self):
    org = Organization(
      staff_contact_person='Ray',
      staff_contact_person_title='Mx',
      staff_contact_phone='555-999-4242',
      staff_contact_email='who@what.z'
    )
    self.assertEqual(org.get_staff_entered_contact_info(), 'Ray, Mx, 555-999-4242, who@what.z')
