# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('WCUser', '0003_user_phone'),
        ('WCLogistics', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='address',
            field=models.CharField(default=b'', max_length=255),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='address',
            name='city',
            field=models.CharField(default=b'', max_length=63),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='address',
            name='own',
            field=models.ForeignKey(to='WCUser.User', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='address',
            name='provice',
            field=models.CharField(default=b'', max_length=15),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='address',
            name='real_name',
            field=models.CharField(default=b'', max_length=255),
            preserve_default=True,
        ),
    ]
