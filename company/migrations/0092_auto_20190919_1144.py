# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-09-19 11:44
from __future__ import unicode_literals

import directory_validators.company
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0091_auto_20190829_1410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.TextField(validators=[directory_validators.company.no_html]),
        ),
    ]