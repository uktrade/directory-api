# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-12-12 15:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0021_auto_20161208_1113'),
    ]

    operations = [
        migrations.AddField(
            model_name='companycasestudy',
            name='testimonial_company',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='companycasestudy',
            name='testimonial_job_title',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='companycasestudy',
            name='testimonial_name',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
    ]
