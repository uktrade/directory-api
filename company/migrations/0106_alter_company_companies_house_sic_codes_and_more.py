# Generated by Django 4.1.9 on 2023-05-26 16:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('company', '0105_company_companies_house_sic_codes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='companies_house_sic_codes',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='company',
            name='expertise_countries',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='company',
            name='expertise_industries',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='company',
            name='expertise_languages',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='company',
            name='expertise_products_services',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='company',
            name='expertise_regions',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='company',
            name='export_destinations',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='company',
            name='has_exported_before',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='hs_codes',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='company',
            name='sectors',
            field=models.JSONField(blank=True, default=list),
        ),
    ]