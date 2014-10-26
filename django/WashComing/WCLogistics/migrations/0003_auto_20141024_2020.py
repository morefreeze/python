# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('WCLogistics', '0002_auto_20141024_1241'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='deleted',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='address',
            name='own',
            field=models.ForeignKey(to='WCUser.User'),
        ),
    ]
