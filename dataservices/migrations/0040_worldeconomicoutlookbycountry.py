# Generated by Django 2.2.28 on 2022-08-02 06:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dataservices', '0039_uktotaltradebycountry_uktradeingoodsbycountry_uktradeinservicesbycountry'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorldEconomicOutlookByCountry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject_code', models.CharField(max_length=20)),
                ('subject_descriptor', models.CharField(max_length=100)),
                ('subject_notes', models.TextField()),
                ('units', models.CharField(max_length=60)),
                ('scale', models.CharField(blank=True, max_length=10, null=True)),
                ('year', models.PositiveSmallIntegerField()),
                ('value', models.DecimalField(blank=True, decimal_places=3, max_digits=18, null=True)),
                ('estimates_start_after', models.PositiveSmallIntegerField(blank=True)),
                ('country', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='dataservices.Country', verbose_name='Countries')),
            ],
            options={
                'verbose_name': 'World economic outlook by country',
            },
        ),
    ]
