# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-08-08 10:05
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('supplier', '0005_auto_20190807_1237'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supplier',
            name='is_company_owner',
        ),
    ]