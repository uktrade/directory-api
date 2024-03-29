# Generated by Django 3.2.16 on 2023-01-18 15:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0002_alter_question_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='choice',
            name='jump',
            field=models.ForeignKey(blank=True, help_text='The question that the user will be shown next if they select this choice,\n         if left blank they will be taken to the next question in order', null=True, on_delete=django.db.models.deletion.CASCADE, to='survey.question'),
        ),
        migrations.AlterField(
            model_name='choice',
            name='label',
            field=models.CharField(help_text='The text that will appear to users when the form is displayed', max_length=255),
        ),
        migrations.AlterField(
            model_name='choice',
            name='value',
            field=models.CharField(help_text='The value that the choice will be saved as if a user selects it', max_length=255),
        ),
    ]
