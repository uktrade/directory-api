# Generated by Django 3.2.16 on 2022-12-07 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='type',
            field=models.CharField(choices=[('RADIO', 'radio'), ('SELECT', 'select'), ('MULTI_SELECT', 'multi_select'), ('SHORT_TEXT', 'short_text'), ('LONG_TEXT', 'long_text')], max_length=255),
        ),
    ]
