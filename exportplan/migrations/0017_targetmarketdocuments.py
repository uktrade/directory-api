# Generated by Django 2.2.13 on 2020-08-17 15:19

import directory_validators.string
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('exportplan', '0016_companyexportplan_adaptation_target_market'),
    ]

    operations = [
        migrations.CreateModel(
            name='TargetMarketDocuments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, null=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, null=True, verbose_name='modified')),
                ('document_name', models.TextField(blank=True, default='', validators=[directory_validators.string.no_html])),
                ('note', models.TextField(blank=True, default='', validators=[directory_validators.string.no_html])),
                ('companyexportplan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target_market_documents', to='exportplan.CompanyExportPlan')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]
