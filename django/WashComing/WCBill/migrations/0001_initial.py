# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('WCUser', '0003_user_phone'),
        ('WCLogistics', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('bid', models.AutoField(serialize=False, primary_key=True)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('get_time', models.DateTimeField()),
                ('return_time', models.DateTimeField()),
                ('status', models.IntegerField(default=0)),
                ('deleted', models.BooleanField(default=False)),
                ('clothes', jsonfield.fields.JSONField(default={})),
                ('ext', jsonfield.fields.JSONField(default=None)),
                ('adr', models.ForeignKey(to='WCLogistics.Address')),
                ('lg', models.ForeignKey(to='WCLogistics.Map')),
                ('own', models.ForeignKey(to='WCUser.User')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
