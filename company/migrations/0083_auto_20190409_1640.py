# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-04-09 16:40
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0082_auto_20190329_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='expertise_products_services',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, help_text='The products and services the company has expertise in.'),
        ),
        migrations.AlterField(
            model_name='company',
            name='expertise_countries',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=[], help_text='The countries that this company has expertise in.'),
        ),
        migrations.AlterField(
            model_name='company',
            name='expertise_languages',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=[], help_text='The languages that this company has expertise in.'),
        ),
        migrations.AlterField(
            model_name='company',
            name='expertise_regions',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=[], help_text='The regions that this company has expertise in.'),
        ),
    ]
