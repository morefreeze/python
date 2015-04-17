# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='own_shop',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
