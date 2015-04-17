# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0004_auto_20150114_0843'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myuser',
            name='email2',
        ),
    ]
