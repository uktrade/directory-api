# Generated by Django 2.2.13 on 2021-01-25 09:43

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exportplan', '0025_auto_20210125_0840'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyexportplan',
            name='ui_progress',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True),
        ),
    ]