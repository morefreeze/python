# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cloth',
            fields=[
                ('cid', models.AutoField(serialize=False, primary_key=True)),
                ('is_leaf', models.BooleanField(default=True)),
                ('fa_cid', models.IntegerField(default=0)),
                ('name', models.CharField(unique=True, max_length=32)),
                ('detail', models.CharField(max_length=255)),
                ('price', models.FloatField()),
                ('deleted', models.BooleanField(default=False)),
                ('ext', jsonfield.fields.JSONField(default={})),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
