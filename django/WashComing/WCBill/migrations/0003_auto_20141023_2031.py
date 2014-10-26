# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('WCBill', '0002_auto_20141023_2028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='status',
            field=models.IntegerField(default=0),
        ),
    ]
