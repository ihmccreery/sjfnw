from django.core.management.base import BaseCommand
from sjfnw.fund.models import Donor


class Command(BaseCommand):

  help = 'Cautiously deletes duplicate donors (will not delete any with a step)'

  def handle(self, *args, **options):
    self.stdout.write('Beginning.\n')
    donors = (Donor.objects.select_related('membership')
                                  .prefetch_related('step_set')
                                  .order_by('firstname', 'lastname',
                                            'membership', '-talked'))
    deleted = 0
    prior = None
    for donor in donors:
      # check if donor matches prev, & has no completed steps
      if (prior and donor.membership == prior.membership and
          donor.firstname == prior.firstname and
          donor.lastname and donor.lastname == prior.lastname and
          not donor.talked):
        if donor.get_next_step():
          self.stdout.write(unicode(donor) + ' matched but has a step. Not deleting.')
        else:
          self.stdout.write('Deleting ' + unicode(donor))
          donor.delete()
          deleted += 1
      prior = donor

    self.stdout.write(deleted ' donors deleted.')

