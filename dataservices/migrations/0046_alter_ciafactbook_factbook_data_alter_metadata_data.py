# Generated by Django 4.1.9 on 2023-05-26 16:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dataservices', '0045_add_uk_trade_agreements_records'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ciafactbook',
            name='factbook_data',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='metadata',
            name='data',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]