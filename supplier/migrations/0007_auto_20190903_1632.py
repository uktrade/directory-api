# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-09-03 16:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supplier', '0006_remove_supplier_is_company_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplier',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='suppliers', to='company.Company'),
        ),
    ]
