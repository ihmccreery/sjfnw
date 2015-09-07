# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Donor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=datetime.datetime(2015, 9, 6, 22, 54, 7, 667508, tzinfo=utc))),
                ('firstname', models.CharField(max_length=100, verbose_name=b'*First name')),
                ('lastname', models.CharField(max_length=100, verbose_name=b'Last name', blank=True)),
                ('amount', models.PositiveIntegerField(null=True, verbose_name=b'*Amount to ask ($)', blank=True)),
                ('likelihood', models.PositiveIntegerField(blank=True, null=True, verbose_name=b'*Estimated likelihood (%)', validators=[django.core.validators.MaxValueValidator(100)])),
                ('talked', models.BooleanField(default=False)),
                ('asked', models.BooleanField(default=False)),
                ('promised', models.PositiveIntegerField(null=True, blank=True)),
                ('promise_reason', models.TextField(default=b'[]', blank=True)),
                ('likely_to_join', models.PositiveIntegerField(blank=True, null=True, choices=[(b'', b'---------'), (3, b'3 - Definitely'), (2, b'2 - Likely'), (1, b'1 - Unlikely'), (0, b'0 - No chance')])),
                ('received_this', models.PositiveIntegerField(default=0, verbose_name=b'Received - current year')),
                ('received_next', models.PositiveIntegerField(default=0, verbose_name=b'Received - next year')),
                ('received_afternext', models.PositiveIntegerField(default=0, verbose_name=b'Received - year after next')),
                ('gift_notified', models.BooleanField(default=False)),
                ('match_expected', models.PositiveIntegerField(default=0, blank=True, verbose_name=b'Match expected ($)', validators=[django.core.validators.MinValueValidator(0)])),
                ('match_company', models.CharField(max_length=255, verbose_name=b'Employer name', blank=True)),
                ('match_received', models.PositiveIntegerField(default=0, verbose_name=b'Match received ($)', blank=True)),
                ('phone', models.CharField(max_length=15, blank=True)),
                ('email', models.EmailField(max_length=100, blank=True)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['firstname', 'lastname'],
            },
        ),
        migrations.CreateModel(
            name='GivingProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('public', models.BooleanField(default=True, help_text=b'Whether this project should show in the dropdown menu for members registering or adding a project to their account.')),
                ('pre_approved', models.TextField(help_text=b'List of member emails, separated by commas.  Anyone who registers using an email on this list will have their account automatically approved.  IMPORTANT: Any syntax error can make this feature stop working; in that case memberships will default to requiring manual approval by an administrator.', blank=True)),
                ('fundraising_training', models.DateTimeField(help_text=b'Date & time of fundraising training.  At this point the app will require members to enter an ask amount & estimated likelihood for each contact.')),
                ('fundraising_deadline', models.DateField(help_text=b'Members will stop receiving reminder emails at this date.')),
                ('fund_goal', models.PositiveIntegerField(default=0, help_text=b"Fundraising goal agreed upon by the group. If 0, it will not be displayed to members and they won't see a group progress chart for money raised.", verbose_name=b'Fundraising goal')),
                ('suggested_steps', models.TextField(default=b'Talk to about project\nInvite to SJF event\nSet up time to meet for the ask\nAsk\nFollow up\nThank', help_text=b'Displayed to users when they add a step.  Put each step on a new line')),
                ('site_visits', models.BooleanField(default=False, help_text=b'If checked, members will only see grants with a screening status of at least "site visit awarded"')),
                ('calendar', models.CharField(help_text=b'Calendar ID of a google calendar - format: ____@group.calendar.google.com', max_length=255, blank=True)),
            ],
            options={
                'ordering': ['-fundraising_deadline'],
            },
        ),
        migrations.CreateModel(
            name='GPSurvey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField()),
                ('giving_project', models.ForeignKey(to='fund.GivingProject')),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(unique=True, max_length=100)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('current', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['first_name', 'last_name'],
            },
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('approved', models.BooleanField(default=False)),
                ('leader', models.BooleanField(default=False)),
                ('copied_contacts', models.BooleanField(default=False)),
                ('completed_surveys', models.CharField(default=b'[]', max_length=255)),
                ('emailed', models.DateField(help_text=b'Last time this member was sent an overdue steps reminder', null=True, blank=True)),
                ('last_activity', models.DateField(help_text=b'Last activity by this user on this membership.', null=True, blank=True)),
                ('notifications', models.TextField(default=b'', blank=True)),
                ('giving_project', models.ForeignKey(to='fund.GivingProject')),
                ('member', models.ForeignKey(to='fund.Member')),
            ],
            options={
                'ordering': ['member'],
            },
        ),
        migrations.CreateModel(
            name='NewsItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=datetime.datetime(2015, 9, 6, 22, 54, 7, 670126, tzinfo=utc))),
                ('updated', models.DateTimeField(default=datetime.datetime(2015, 9, 6, 22, 54, 7, 670165, tzinfo=utc))),
                ('summary', models.TextField()),
                ('membership', models.ForeignKey(to='fund.Membership')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('session', models.CharField(max_length=255)),
                ('giving_project', models.ForeignKey(to='fund.GivingProject')),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime(2015, 9, 6, 22, 54, 7, 671089, tzinfo=utc), null=True, blank=True)),
                ('title', models.CharField(max_length=255)),
                ('summary', models.TextField(blank=True)),
                ('link', models.URLField()),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime(2015, 9, 6, 22, 54, 7, 669172, tzinfo=utc))),
                ('date', models.DateField(verbose_name=b'Date')),
                ('description', models.CharField(max_length=255, verbose_name=b'Description')),
                ('completed', models.DateTimeField(null=True, blank=True)),
                ('asked', models.BooleanField(default=False)),
                ('promised', models.PositiveIntegerField(null=True, blank=True)),
                ('donor', models.ForeignKey(to='fund.Donor')),
            ],
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=datetime.datetime(2015, 9, 6, 22, 54, 7, 672605, tzinfo=utc))),
                ('updated', models.DateTimeField(default=datetime.datetime(2015, 9, 6, 22, 54, 7, 672643, tzinfo=utc))),
                ('updated_by', models.CharField(max_length=100, blank=True)),
                ('title', models.CharField(help_text=b"Descriptive summary to aid in sharing survey templates between projects. For admin site only. E.g. 'GP session evaluation', 'Race workshop evaluation', etc.", max_length=255)),
                ('intro', models.TextField(default=b"Please fill out this quick survey to let us know how the last meeting went.  Responses are anonymous, and once you fill out the survey you'll be taken to your regular home page.", help_text=b'Introductory text to display before the questions when form is shown to GP members.')),
                ('questions', models.TextField(default=b'[{"question": "Did we meet our goals? (1=not at all, 5=completely)", "choices": ["1", "2", "3", "4", "5"]}]', help_text=b"Leave all of a question' choices blank if you want a write-in response instead of multiple choice")),
            ],
        ),
        migrations.CreateModel(
            name='SurveyResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=datetime.datetime(2015, 9, 6, 22, 54, 7, 674207, tzinfo=utc))),
                ('responses', models.TextField()),
                ('gp_survey', models.ForeignKey(to='fund.GPSurvey')),
            ],
        ),
        migrations.AddField(
            model_name='projectresource',
            name='resource',
            field=models.ForeignKey(to='fund.Resource'),
        ),
        migrations.AddField(
            model_name='member',
            name='giving_project',
            field=models.ManyToManyField(to='fund.GivingProject', through='fund.Membership'),
        ),
        migrations.AddField(
            model_name='gpsurvey',
            name='survey',
            field=models.ForeignKey(to='fund.Survey'),
        ),
        migrations.AddField(
            model_name='givingproject',
            name='resources',
            field=models.ManyToManyField(to='fund.Resource', null=True, through='fund.ProjectResource', blank=True),
        ),
        migrations.AddField(
            model_name='givingproject',
            name='surveys',
            field=models.ManyToManyField(to='fund.Survey', null=True, through='fund.GPSurvey', blank=True),
        ),
        migrations.AddField(
            model_name='donor',
            name='membership',
            field=models.ForeignKey(to='fund.Membership'),
        ),
        migrations.AlterUniqueTogether(
            name='membership',
            unique_together=set([('giving_project', 'member')]),
        ),
    ]
