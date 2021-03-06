# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-11-10 16:49
from __future__ import unicode_literals

import json

from django.db import migrations


def ensure_sector_list(apps, schema_editor):
    """
    We used to do `json.dumps` before saving the sectors. This was not needed
    and resulted in the value being dumped to json twice.
    """
    CompanyModel = apps.get_model("company", "Company")
    for company in CompanyModel.objects.all():
        if isinstance(company.sectors, str):
            company.sectors = json.loads(company.sectors)
            company.save()


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0009_auto_20161031_1504'),
    ]

    operations = [
        migrations.RunPython(ensure_sector_list)
    ]
