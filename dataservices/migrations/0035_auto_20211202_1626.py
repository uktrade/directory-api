# Generated by Django 2.2.24 on 2021-12-02 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataservices', '0034_auto_20211202_1603'),
    ]

    operations = [
        migrations.RenameField(
            model_name='easeofdoingbusiness',
            old_name='year_2019',
            new_name='year',
        ),
        migrations.RemoveField(
            model_name='easeofdoingbusiness',
            name='country_code',
        ),
        migrations.RemoveField(
            model_name='easeofdoingbusiness',
            name='country_name',
        ),
        migrations.AddField(
            model_name='easeofdoingbusiness',
            name='value',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=15, null=True),
        ),
    ]
