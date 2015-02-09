from django.contrib.auth.models import User

from sjfnw.fund import models
from sjfnw.grants.models import ProjectApp

import logging
logger = logging.getLogger('sjfnw')


def get_block_content(membership, get_steps=True):
  """ Provide upper block content for the 3 main views

  Args:
    membership: current Membership
    get_steps: include list of upcoming steps or not

  Returns: List with
    steps: 2 closest upcoming steps
    news: news items, sorted by date descending
    grants: ProjectApps ordered by org name
  """

  blocks = []
  # upcoming steps
  if get_steps:
    blocks.append(models.Step.objects
        .select_related('donor')
        .filter(donor__membership=membership, completed__isnull=True)
        .order_by('date')[:2])

  # project news
  blocks.append(models.NewsItem.objects
      .filter(membership__giving_project=membership.giving_project)
      .order_by('-date')[:25])

  # grants
  p_apps = ProjectApp.objects.filter(giving_project=membership.giving_project)
  p_apps = p_apps.select_related('giving_project', 'application',
      'application__organization')
  # never show screened out by sub-committee
  p_apps = p_apps.exclude(application__pre_screening_status=45)
  if membership.giving_project.site_visits == 1:
    logger.info('Filtering grants for site visits')
    p_apps = p_apps.filter(screening_status__gte=70)
  p_apps = p_apps.order_by('application__organization__name')
  blocks.append(p_apps)

  return blocks


def is_pre_approved(email, giving_project):
  """ Checks new membership for pre-approval status """
  if giving_project.pre_approved:
    approved_emails = [email.strip().lower() for email in giving_project.pre_approved.split(',')]
    logger.info(u'Checking pre-approval for %s in %s. Pre-approved list: %s',
                email, giving_project, giving_project.pre_approved)
    if email in approved_emails:
      return True
  return False

def create_user(email, password, first_name, last_name):
  error, user, member = None, None, None

  # check if Member already
  if models.Member.objects.filter(email=email):
    error = 'That email is already registered.  <a href="/fund/login/">Login</a> instead.'
    logger.warning(email + ' tried to re-register')

  # check User already but not Member
  elif User.objects.filter(username=email):
    error = 'That email is already registered through Social Justice Fund\'s online grant application.  Please use a different email address.'
    logger.warning('User already exists, but not Member: ' + email)

  else:
    # ok to register - create User and Member
    user = User.objects.create_user(email, email, password)
    user.first_name = first_name
    user.last_name = last_name
    user.save()
    member = models.Member(email=email, first_name=first_name,
                           last_name=last_name)
    member.save()
    logger.info('Registration - user and member objects created for ' + email)

  return error, user, member

def create_membership(member, giving_project, notif=''):
  error, membership = None, None

  approved = is_pre_approved(member.email, giving_project)

  membership, new = models.Membership.objects.get_or_create(
      member=member, giving_project=giving_project,
      defaults={
        'approved': approved, 'notifications': notif
      }
  )

  if not new:
    error = 'You are already registered with that giving project.'
  else:
    member.current = membership.pk
    member.save()

  return error, membership

