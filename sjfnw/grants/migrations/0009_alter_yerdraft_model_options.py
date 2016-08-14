# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grants', '0008_auto_20160803_1458'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='yerdraft',
            options={'verbose_name': 'Draft year-end report'},
        ),
    ]
