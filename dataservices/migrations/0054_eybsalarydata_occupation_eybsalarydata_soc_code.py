# Generated by Django 4.2.11 on 2024-06-03 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataservices', '0053_alter_eybsalarydata_mean_salary_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='eybsalarydata',
            name='occupation',
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='eybsalarydata',
            name='soc_code',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]