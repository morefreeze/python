# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('WCBill', '0005_auto_20141024_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
