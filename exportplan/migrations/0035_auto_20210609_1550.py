# Generated by Django 2.2.22 on 2021-06-09 15:50

import core.helpers
import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exportplan', '0034_exportplandownloads'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='exportplandownloads',
            options={'verbose_name_plural': 'Exportplan downloads'},
        ),
        migrations.RemoveField(
            model_name='companyexportplan',
            name='sectors',
        ),
        migrations.RemoveField(
            model_name='companyexportplan',
            name='target_markets',
        ),
        migrations.AlterField(
            model_name='exportplandownloads',
            name='pdf_file',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(), upload_to=core.helpers.PathAndRename(default_ext='.pdf', sub_path='exportplan_pdfs')),
        ),
        migrations.DeleteModel(
            name='ExportPlanActions',
        ),
    ]