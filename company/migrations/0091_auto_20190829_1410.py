# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-29 14:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0090_auto_20190829_0845'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='collaborationinvite',
            options={'get_latest_by': 'modified', 'ordering': ('-modified', '-created')},
        ),
        migrations.AlterUniqueTogether(
            name='collaborationinvite',
            unique_together=set([]),
        ),
    ]