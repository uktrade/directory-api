# Generated by Django 4.2.11 on 2024-06-03 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataservices', '0052_rename_dataworkspace_ingestion_year_eybcommercialpropertyrent_dataset_year_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eybsalarydata',
            name='mean_salary',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='eybsalarydata',
            name='median_salary',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]