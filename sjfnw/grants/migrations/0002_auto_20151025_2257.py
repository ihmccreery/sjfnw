# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('grants', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='yearendreport',
            name='submitted',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='yerdraft',
            name='modified',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
