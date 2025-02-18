# Generated by Django 4.2.16 on 2024-12-04 16:36

from django.db import migrations, models
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('exporting', '0007_add_region_ids_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='Postcode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, null=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, null=True, verbose_name='modified'
                    ),
                ),
                ('post_code', models.TextField()),
                ('region', models.TextField(blank=True, null=True)),
                ('european_electoral_region', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ['post_code', 'region', 'european_electoral_region'],
                'indexes': [models.Index(fields=['post_code'], name='exporting_p_post_co_927fba_idx')],
            },
        ),
    ]
