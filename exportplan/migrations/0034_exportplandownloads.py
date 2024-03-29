# Generated by Django 2.2.20 on 2021-05-04 10:23

import core.helpers
from core.storage import private_storage
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('exportplan', '0033_auto_20210408_1200'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportplanDownloads',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, null=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, null=True, verbose_name='modified')),
                ('pdf_file', models.FileField(storage=private_storage, upload_to=core.helpers.PathAndRename(sub_path='exportplan_pdfs'))),
                ('companyexportplan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exportplan_downloads', to='exportplan.CompanyExportPlan')),
            ],
            options={
                'verbose_name_plural': 'Company Objectives',
            },
        ),
    ]
