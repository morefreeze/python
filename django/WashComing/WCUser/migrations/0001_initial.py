# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('uid', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('token', models.CharField(max_length=32)),
                ('openauth', models.CharField(max_length=255)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('last_time', models.DateTimeField(auto_now=True)),
                ('score', models.IntegerField(default=0)),
                ('invited_uid', models.IntegerField(default=0)),
                ('deleted', models.BooleanField(default=False)),
                ('ext', jsonfield.fields.JSONField(default={})),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
