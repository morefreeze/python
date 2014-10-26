# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('WCBill', '0003_auto_20141023_2031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='lg',
            field=models.ForeignKey(to='WCLogistics.Map', null=True),
        ),
    ]
