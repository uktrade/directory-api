# Generated by Django 4.1.13 on 2024-01-15 11:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('company', '0107_companycasestudy_is_published_case_study'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyuser',
            name='company',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='company_users',
                to='company.company',
            ),
        ),
    ]
