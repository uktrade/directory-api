# Generated by Django 3.2.16 on 2023-03-17 12:26

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exporting', '0006_auto_20220613_1725'),
    ]

    operations = [
        migrations.AddField(
            model_name='office',
            name='region_ids',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), help_text='Regions need to be separated by commas.', null=True, size=None),
        ),
        migrations.AlterField(
            model_name='office',
            name='region_id',
            field=models.TextField(blank=True, null=True),
        ),
    ]