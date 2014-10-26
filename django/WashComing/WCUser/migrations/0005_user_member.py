# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('WCUser', '0004_user_default_adr'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='member',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
