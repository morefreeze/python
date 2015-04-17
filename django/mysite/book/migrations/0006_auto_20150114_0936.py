# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0005_remove_myuser_email2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myuser',
            name='date_of_birth',
        ),
        migrations.RemoveField(
            model_name='myuser',
            name='is_admin',
        ),
    ]
