# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-11-08 15:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_auto_20161129_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='mobile_number',
            field=models.CharField(max_length=20, unique=True, null=True, blank=True,),
        ),
        migrations.RemoveField(
            model_name='user',
            name='referrer',
        ),
    ]
