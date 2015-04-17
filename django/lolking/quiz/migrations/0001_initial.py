# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('qid', models.AutoField(serialize=False, primary_key=True)),
                ('correct', models.IntegerField(default=-1)),
                ('question', models.CharField(max_length=1023)),
                ('answer', models.CharField(max_length=31)),
                ('pic', models.CharField(max_length=1023)),
                ('ans_list', jsonfield.fields.JSONField(default=[])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
