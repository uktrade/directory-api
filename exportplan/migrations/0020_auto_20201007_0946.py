# Generated by Django 2.2.13 on 2020-10-07 09:46

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exportplan', '0019_auto_20200930_1545'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='companyexportplan',
            name='rationale',
        ),
        migrations.AddField(
            model_name='companyexportplan',
            name='objectives',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, null=True),
        ),
    ]
