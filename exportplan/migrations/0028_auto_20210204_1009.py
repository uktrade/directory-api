# Generated by Django 2.2.13 on 2021-02-04 10:09

import directory_validators.string
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('exportplan', '0027_companyexportplan_getting_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyexportplan',
            name='travel_business_policies',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.CreateModel(
            name='BusinessTrips',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, null=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, null=True, verbose_name='modified')),
                ('note', models.TextField(blank=True, default='', validators=[directory_validators.string.no_html])),
                ('companyexportplan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='business_trips', to='exportplan.CompanyExportPlan')),
            ],
            options={
                'verbose_name_plural': 'Business Trips',
            },
        ),
    ]