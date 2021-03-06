# Generated by Django 2.2.10 on 2020-03-13 15:30

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('exportplan', '0003_auto_20200219_1332'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportPlanActions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, null=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, null=True, verbose_name='modified')),
                ('owner', models.PositiveIntegerField(default=None, null=True, verbose_name='sso user.sso_id')),
                ('due_date', models.DateField(blank=True, null=True)),
                ('is_reminders_on', models.BooleanField(default=False)),
                ('action_type', models.CharField(choices=[('TARGET_MARKETS', 'Target Markets')], default='TARGET_MARKETS', max_length=15)),
                ('companyexportplan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='exportplan.CompanyExportPlan')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]
