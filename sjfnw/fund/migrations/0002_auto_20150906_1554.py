# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('fund', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donor',
            name='added',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 6, 22, 54, 32, 560768, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='newsitem',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 6, 22, 54, 32, 563390, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='newsitem',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 6, 22, 54, 32, 563428, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='resource',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 6, 22, 54, 32, 564349, tzinfo=utc), null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='step',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 6, 22, 54, 32, 562442, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='survey',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 6, 22, 54, 32, 565859, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='survey',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 6, 22, 54, 32, 565998, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='surveyresponse',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 6, 22, 54, 32, 567550, tzinfo=utc)),
        ),
    ]
