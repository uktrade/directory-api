# Generated by Django 2.2.10 on 2020-02-19 13:32

import directory_validators.string
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('exportplan', '0002_auto_20200214_1012'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyexportplan',
            name='compliance',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='companyexportplan',
            name='consumer_demand',
            field=models.TextField(blank=True, default='', null=True, validators=[directory_validators.string.no_html]),
        ),
        migrations.AddField(
            model_name='companyexportplan',
            name='export_certificates',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='companyexportplan',
            name='planned_review',
            field=models.TextField(blank=True, default='', null=True, validators=[directory_validators.string.no_html]),
        ),
        migrations.AddField(
            model_name='companyexportplan',
            name='promotion_channels',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='companyexportplan',
            name='rational',
            field=models.TextField(blank=True, default='', null=True, validators=[directory_validators.string.no_html]),
        ),
        migrations.AddField(
            model_name='companyexportplan',
            name='resource_needed',
            field=models.TextField(blank=True, default='', null=True, validators=[directory_validators.string.no_html]),
        ),
        migrations.AddField(
            model_name='companyexportplan',
            name='route_to_markets',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='companyexportplan',
            name='sectors',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AddField(
            model_name='companyexportplan',
            name='spend_marketing',
            field=models.FloatField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='companyexportplan',
            name='target_countries',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='companyexportplan',
            name='rules_regulations',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, null=True),
        ),
        migrations.CreateModel(
            name='CompanyObjectives',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, null=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, null=True, verbose_name='modified')),
                ('description', models.TextField(blank=True, default='', null=True, validators=[directory_validators.string.no_html])),
                ('owner', models.PositiveIntegerField(default=None, null=True, verbose_name='sso user.sso_id')),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('companyexportplan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='objectives', to='exportplan.CompanyExportPlan')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]
