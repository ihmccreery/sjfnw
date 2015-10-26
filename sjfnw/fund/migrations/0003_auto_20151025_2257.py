# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('fund', '0002_auto_20150906_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donor',
            name='added',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='givingproject',
            name='fundraising_training',
            field=models.DateTimeField(help_text=b'Date & time of fundraising training. At this point the app will require members to enter an ask amount & estimated likelihood for each contact.'),
        ),
        migrations.AlterField(
            model_name='givingproject',
            name='pre_approved',
            field=models.TextField(help_text=b'List of member emails, separated by commas. Anyone who registers using an email on this list will have their account automatically approved.  IMPORTANT: Any syntax error can make this feature stop working; in that case memberships will default to requiring manual approval by an administrator.', blank=True),
        ),
        migrations.AlterField(
            model_name='givingproject',
            name='resources',
            field=models.ManyToManyField(to='fund.Resource', through='fund.ProjectResource', blank=True),
        ),
        migrations.AlterField(
            model_name='givingproject',
            name='suggested_steps',
            field=models.TextField(default=b'Talk to about project\nInvite to SJF event\nSet up time to meet for the ask\nAsk\nFollow up\nThank', help_text=b'Displayed to users when they add a step. Put each step on a new line'),
        ),
        migrations.AlterField(
            model_name='givingproject',
            name='surveys',
            field=models.ManyToManyField(to='fund.Survey', through='fund.GPSurvey', blank=True),
        ),
        migrations.AlterField(
            model_name='newsitem',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='newsitem',
            name='updated',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='resource',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='step',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='survey',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='survey',
            name='questions',
            field=models.TextField(default=b'[{"question": "Did we meet our goals? (1=not at all, 5=completely)", "choices": ["1", "2", "3", "4", "5"]}]', help_text=b"Leave all of a question's choices blank if you want a write-in response instead of multiple choice"),
        ),
        migrations.AlterField(
            model_name='survey',
            name='updated',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='surveyresponse',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
