# Generated by Django 2.2.13 on 2020-08-04 10:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exportplan', '0011_auto_20200714_1531'),
    ]

    operations = [
        migrations.RenameField(
            model_name='companyexportplan',
            old_name='route_to_markets',
            new_name='marketing_approach',
        ),
    ]
