# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0007_myuser_own_shop'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('bid', models.AutoField(serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
