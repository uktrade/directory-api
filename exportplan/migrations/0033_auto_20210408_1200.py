# Generated by Django 2.2.19 on 2021-04-08 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exportplan', '0032_update_ui_progress'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fundingcreditoptions',
            name='amount',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
