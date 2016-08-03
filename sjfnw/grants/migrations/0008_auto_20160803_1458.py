# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sjfnw.grants.models


class Migration(migrations.Migration):

    dependencies = [
        ('grants', '0007_fill_yer_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='givingprojectgrant',
            name='first_yer_due',
            field=models.DateField(help_text=b'If this is a two-year grant, the second YER will automatically be due one year after the first', verbose_name=b'Year-end report due date'),
        ),
        migrations.AlterField(
            model_name='grantapplication',
            name='narrative2',
            field=models.TextField(help_text=b"Your organization's leadership body is the group of people who together make strategic decisions about the organization's direction, provide oversight and guidance, and are ultimately responsible for the organization's mission and ability to carry out its mission. In most cases, this will be a Board of Directors, but it might also be a steering committee, collective, or other leadership structure.", verbose_name=b'Social Justice Fund prioritizes groups that are led by the people most impacted by the issues the group is working on, and continually build leadership from within their own communities.<ul><li>Who are the communities most directly impacted by the issues your organization addresses?</li><li>How are those communities involved in the leadership of your organization, and how does your organization remain accountable to those communities?</li><li>What is your organization\'s <span class="has-more-info" id="nar-2">leadership body?</span></li></ul>', validators=[sjfnw.grants.models.WordLimitValidator(200)]),
        ),
        migrations.AlterField(
            model_name='grantapplication',
            name='narrative4',
            field=models.TextField(help_text=b'<ul><li>A goal is what your organization wants to achieve or accomplish. You may have both internal goals (how this work will impact your organization) and external goals (how this work will impact your broader community).</li><li>An objective is generally narrower and more specific than a goal, like a stepping stone along the way.</li><li>A strategy is a road map for achieving your goal. How will you get there? A strategy will generally encompass multiple activities or tactics.</li></ul>', verbose_name=b'Please describe your workplan, covering at least the next 12 months. (You will list the activities and objectives in the timeline form below.)<ul><li>What are your overall <span class="has-more-info" id="nar-4">goals, objectives and strategies</span> for the coming year?</li><li>How will you assess whether you have met your goals and objectives?</li></ul>', validators=[sjfnw.grants.models.WordLimitValidator(300)]),
        ),
    ]
