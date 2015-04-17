# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0002_auto_20141229_1733'),
    ]

    operations = [
        migrations.RenameField(
            model_name='quiz',
            old_name='correct',
            new_name='which',
        ),
    ]
