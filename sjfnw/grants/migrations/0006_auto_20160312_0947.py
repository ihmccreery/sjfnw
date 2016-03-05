# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import sjfnw.grants.models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('grants', '0005_grant_application_overflow'),
    ]

    operations = [
        migrations.AddField(
            model_name='givingprojectgrant',
            name='first_yer_due',
            field=models.DateField(default=datetime.datetime.fromtimestamp(0), help_text=b'If this is a two-year grant, the second YER will automatically be due one year after the first', verbose_name=b'Year-end report due-date'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='grantapplicationoverflow',
            name='grant_application',
            field=models.OneToOneField(related_name='overflow', to='grants.GrantApplication'),
        ),
        migrations.AlterField(
            model_name='grantapplicationoverflow',
            name='two_year_question',
            field=models.TextField(blank=True, validators=[sjfnw.grants.models.WordLimitValidator(300)]),
        ),
    ]
