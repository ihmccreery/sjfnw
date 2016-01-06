# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grants', '0002_auto_20151025_2257'),
    ]

    operations = [
        migrations.AddField(
            model_name='grantcycle',
            name='two_year_grants',
            field=models.BooleanField(default=False, verbose_name=b'Cycles associated with two-year grants have an extra question in their application.'),
        ),
        migrations.AddField(
            model_name='grantcycle',
            name='two_year_question',
            field=models.TextField(default=b'This grant will provide funding for two years. While we know it can be difficult to predict your work beyond a year, please give us an idea of what the second year might look like.<ol><li>What overall goals and strategies do you forecast in the second year?</li><li>How will the second year of this grant build on your work in the first year?</li></ol>', verbose_name=b'This question is only shown if "Two year grants" is checked', blank=True),
        ),
    ]
