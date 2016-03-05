# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def fill_yer_due(apps, schema_editor):
  """ Populate new first_yer_due field using old method - agreement mailed + 1 yr """

  GivingProjectGrant = apps.get_model("grants", "GivingProjectGrant")

  for gpg in GivingProjectGrant.objects.filter(agreement_mailed__isnull=False):
    gpg.first_yer_due = gpg.agreement_mailed.replace(year=gpg.agreement_mailed.year + 1)
    gpg.save()

class Migration(migrations.Migration):

  dependencies = [
    ('grants', '0006_auto_20160312_0947'),
  ]

  operations = [
      migrations.RunPython(fill_yer_due)
  ]
