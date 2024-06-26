# Generated by Django 4.2.11 on 2024-05-16 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataservices', '0049_market'),
    ]

    operations = [
        migrations.CreateModel(
            name='EYBStatistaCommercialPropertyRent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geo_description', models.CharField()),
                ('vertical', models.CharField()),
                ('sub_vertical', models.CharField()),
                (
                    'gbp_per_square_foot_per_month',
                    models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True),
                ),
                ('square_feet', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('gbp_per_month', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('dataworkspace_ingestion_year', models.SmallIntegerField(blank=True, null=True)),
            ],
        ),
    ]
