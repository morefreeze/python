# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='answer',
            field=models.CharField(default=b'', max_length=31, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='pic',
            field=models.CharField(default=b'', max_length=1023, blank=True),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='question',
            field=models.CharField(default=b'', max_length=1023, blank=True),
        ),
    ]
