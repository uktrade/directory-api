# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2017-01-17 14:51
from __future__ import unicode_literals

import core.helpers
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0029_auto_20170111_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='logo',
            field=models.ImageField(blank=True, default='', upload_to=core.helpers.PathAndRename(sub_path='/company_logos')),
        ),
        migrations.AlterField(
            model_name='companycasestudy',
            name='image_one',
            field=models.ImageField(blank=True, default='', upload_to=core.helpers.PathAndRename(sub_path='/supplier_case_study')),
        ),
        migrations.AlterField(
            model_name='companycasestudy',
            name='image_three',
            field=models.ImageField(blank=True, default='', upload_to=core.helpers.PathAndRename(sub_path='/supplier_case_study')),
        ),
        migrations.AlterField(
            model_name='companycasestudy',
            name='image_two',
            field=models.ImageField(blank=True, default='', upload_to=core.helpers.PathAndRename(sub_path='/supplier_case_study')),
        ),
    ]
