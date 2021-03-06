# Generated by Django 2.2.7 on 2019-11-21 11:42

import directory_validators.string
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0099_auto_20191108_1638'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='number',
            field=models.CharField(blank=True, help_text='For companies registered in companies house this is their companies house number. For non-companies house companies this is a randomly string.', max_length=8, null=True, unique=True, validators=[directory_validators.string.no_html]),
        ),
        migrations.AlterField(
            model_name='companyuser',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_users', to='company.Company'),
        ),
    ]
