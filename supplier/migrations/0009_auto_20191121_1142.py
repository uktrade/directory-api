# Generated by Django 2.2.7 on 2019-11-21 11:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supplier', '0008_auto_20190918_1043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplier',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='suppliers', to='company.Company'),
        ),
    ]
