# Generated by Django 2.2.13 on 2020-07-14 14:31

import directory_validators.string
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exportplan', '0009_remove_companyexportplan_planned_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyexportplan',
            name='research_competition',
            field=models.TextField(blank=True, default='', null=True, validators=[directory_validators.string.no_html]),
        ),
        migrations.AddField(
            model_name='companyexportplan',
            name='research_consumer_demand',
            field=models.TextField(blank=True, default='', null=True, validators=[directory_validators.string.no_html]),
        ),
        migrations.AddField(
            model_name='companyexportplan',
            name='research_product_trends',
            field=models.TextField(blank=True, default='', null=True, validators=[directory_validators.string.no_html]),
        ),
        migrations.AddField(
            model_name='companyexportplan',
            name='research_unique_selling',
            field=models.TextField(blank=True, default='', null=True, validators=[directory_validators.string.no_html]),
        ),
    ]