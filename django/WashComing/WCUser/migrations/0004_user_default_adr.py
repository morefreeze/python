# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('WCLogistics', '0002_auto_20141024_1241'),
        ('WCUser', '0003_user_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='default_adr',
            field=models.OneToOneField(null=True, to='WCLogistics.Address'),
            preserve_default=True,
        ),
    ]
