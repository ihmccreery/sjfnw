# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sjfnw.grants.models


class Migration(migrations.Migration):

    dependencies = [
        ('grants', '0004_auto_20160105_2001'),
    ]

    operations = [
        migrations.CreateModel(
            name='GrantApplicationOverflow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('two_year_question', models.TextField(blank=True, validators=[sjfnw.grants.models.WordLimitValidator(500)])),
            ],
        ),
        migrations.RemoveField(
            model_name='grantapplication',
            name='two_year_question',
        ),
        migrations.AddField(
            model_name='grantapplicationoverflow',
            name='grant_application',
            field=models.OneToOneField(to='grants.GrantApplication'),
        ),
    ]
