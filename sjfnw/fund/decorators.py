from functools import wraps
import logging

from django.shortcuts import redirect
from django.utils.decorators import available_attrs

from sjfnw import constants as c

logger = logging.getLogger('sjfnw')

def approved_membership(function=None):
  """ Allows access to view only if request.membership_status is c.APPROVED

    If not allowing access to view, redirects to appropriate settings/notice page

    Should be used with @login_required
    Relies on data set by MembershipMiddleware

    Returns decorator for wrapping the view
  """

  def decorator(view_func):

    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):

      if request.membership_status == c.APPROVED:
        return view_func(request, *args, **kwargs)

      elif request.membership_status == c.NO_APPROVED:
        logger.info('Membership(s) not approved, redirecting to pending')
        return redirect('/fund/pending')

      elif request.membership_status == c.NO_MEMBERSHIP:
        logger.info('No memberships, redirecting to projects page')
        return redirect('/fund/projects')

      else:
        return redirect('/fund/not-member')

    return _wrapped_view
  return decorator
