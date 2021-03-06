# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-07-18 09:27
from __future__ import unicode_literals

from django.db import migrations


def forwards(apps, schema_editor):
    Company = apps.get_model('company', 'Company')
    yes = ['YES', 'ONE_TWO_YEARS_AGO', 'OVER_TWO_YEARS_AGO']
    for company in Company.objects.all():
        company.has_exported_before = company.export_status in yes
        company.save()


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0050_company_has_exported_before'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=migrations.RunPython.noop)
    ]
