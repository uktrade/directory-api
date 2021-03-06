# Generated by Django 2.2.13 on 2021-01-21 13:25

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('exportplan', '0023_auto_20210112_1317'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyexportplan',
            name='funding_and_credit',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.CreateModel(
            name='FundingCreditOptions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, null=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, null=True, verbose_name='modified')),
                ('funding_option', models.CharField(blank=True, choices=[('bank-loan', 'Bank loan'), ('government', 'Finance support from government'), ('platforms', 'Finance platforms'), ('p-p', 'Peer-to-peer loan'), ('equity', 'Equity finance'), ('other', 'Other')], default='', max_length=30, null=True)),
                ('amount', models.FloatField(blank=True, default=0.0, null=True)),
                ('companyexportplan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='funding_credit_options', to='exportplan.CompanyExportPlan')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]
