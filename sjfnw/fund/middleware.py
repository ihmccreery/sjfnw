import logging

from sjfnw import constants as c
from sjfnw.fund import models

logger = logging.getLogger('sjfnw')

class MembershipMiddleware(object):
  """ Gathers info on the member/ship of current user, stores it on the request

    Sets following on request:
      .membership_status
        0 c.NO_MEMBER      no member object
        1 c.NO_MEMBERSHIP  no membership objects associated w/member
        2 c.NO_APPROVED    no approved memberships
        3 c.APPROVED       active membership is approved
      .member       pointer to model (or None)
      .membership   pointer to model (or None)

    May change member.current if:
      member had no membership with that id, but has other memberships
        -> the first one will be used (first approved one, if possible)
      current is not approved, but 1+ other memberships are
        -> first approved membership will be used

    Returns None (never prevents next middleware/view from executing)
  """

  def process_view(self, request, view_func, view_args, view_kwargs): # pylint: disable=unused-argument
    # only run on fund views
    if not 'fund' in view_func.__module__:
      return None

    request.member = None
    request.membership = None
    request.membership_status = -1

    if not request.user.is_authenticated():
      return None

    member = models.Member.objects.filter(email=request.user.username).first()

    if not member:
      logger.warning('No member object with email of %s', request.user.username)
      request.membership_status = c.NO_MEMBER
      return None

    membership = (models.Membership.objects
        .select_related()
        .filter(member=member, pk=member.current)
        .first())

    # if member.current doesn't exist, try to find another membership
    if not membership:
      all_memberships = member.membership_set.all()
      if all_memberships:
        logger.warning('Invalid member.current (m:%d, c:%d)', member.pk, member.current)
        membership = all_memberships[0]
      else:
        logger.info('%s has no memberships', member)
        request.member = member
        request.membership_status = c.NO_MEMBERSHIP
        return None

    # if membership is not approved, look for one that is
    if not membership.approved:
      logger.warning('Current membership not approved')
      membership = member.membership_set.filter(approved=True).first() or membership

    # update member.current if applicable
    if member.current != membership.pk:
      member.current = membership.pk
      member.save()

    if membership.approved:
      request.membership_status = c.APPROVED
    else:
      request.membership_status = c.NO_APPROVED

    request.member = member
    request.membership = membership

    return None
