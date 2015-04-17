# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0002_myuser_own_shop'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myuser',
            name='own_shop',
        ),
    ]
