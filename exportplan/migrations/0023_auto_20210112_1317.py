# Generated by Django 2.2.13 on 2021-01-12 13:17

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exportplan', '0022_auto_20201116_1607'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyexportplan',
            name='direct_costs',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='companyexportplan',
            name='overhead_costs',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='companyexportplan',
            name='total_cost_and_price',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True),
        ),
    ]