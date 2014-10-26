# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('WCBill', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='clothes',
            field=jsonfield.fields.JSONField(default=None),
        ),
        migrations.AlterField(
            model_name='bill',
            name='status',
            field=models.IntegerField(),
        ),
    ]
