# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-11-24 19:23
from __future__ import unicode_literals

import core.helpers
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0012_auto_20161124_1907'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyCaseStudy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=1000)),
                ('sector', models.CharField(choices=[('AEROSPACE', 'Aerospace'), ('AGRICULTURE_HORTICULTURE_AND_FISHERIES', 'Agriculture, horticulture and fisheries'), ('AIRPORTS', 'Airports'), ('AUTOMOTIVE', 'Automotive'), ('BIOTECHNOLOGY_AND_PHARMACEUTICALS', 'Biotechnology and pharmaceuticals'), ('BUSINESS_AND_CONSUMER_SERVICES', 'Business and consumer services'), ('CHEMICALS', 'Chemicals'), ('CLOTHING_FOOTWEAR_AND_FASHION', 'Clothing, footwear and fashion'), ('COMMUNICATIONS', 'Communications'), ('CONSTRUCTION', 'Construction'), ('CREATIVE_AND_MEDIA', 'Creative and media'), ('DEFENCE', 'Defence'), ('EDUCATION_AND_TRAINING', 'Education and training'), ('ELECTRONICS_AND_IT_HARDWARE', 'Electronics and IT hardware'), ('ENVIRONMENT', 'Environment'), ('FINANCIAL_AND_PROFESSIONAL_SERVICES', 'Financial and professional services'), ('FOOD_AND_DRINK', 'Food and drink'), ('GIFTWARE_JEWELLERY_AND_TABLEWARE', 'Giftware, jewellery and tableware'), ('GLOBAL_SPORTS_INFRASTRUCTURE', 'Global sports infrastructure'), ('HEALTHCARE_AND_MEDICAL', 'Healthcare and medical'), ('HOUSEHOLD_GOODS_FURNITURE_AND_FURNISHINGS', 'Household goods, furniture and furnishings'), ('LEISURE_AND_TOURISM', 'Leisure and tourism'), ('MARINE', 'Marine'), ('MECHANICAL_ELECTRICAL_AND_PROCESS_ENGINEERING', 'Mechanical electrical and process engineering'), ('METALLURGICAL_PROCESS_PLANT', 'Metallurgical process plant'), ('METALS_MINERALS_AND_MATERIALS', 'Metals, minerals and materials'), ('MINING', 'Mining'), ('OIL_AND_GAS', 'Oil and gas'), ('PORTS_AND_LOGISTICS', 'Ports and logistics'), ('POWER', 'Power'), ('RAILWAYS', 'Railways'), ('RENEWABLE_ENERGY', 'Renewable energy'), ('RETAIL_AND_LUXURY', 'Retail and luxury'), ('SECURITY', 'Security'), ('SOFTWARE_AND_COMPUTER_SERVICES', 'Software and computer services'), ('TEXTILES_INTERIOR_TEXTILES_AND_CARPETS', 'Textiles, interior textiles and carpets'), ('WATER', 'Water')], max_length=100)),
                ('website', models.URLField(blank=True, default='', max_length=255, null=True)),
                ('year', models.CharField(max_length=4)),
                ('keywords', models.TextField()),
                ('image_one', models.FileField(blank=True, null=True, upload_to=core.helpers.PathAndRename(sub_path='/supplier_case_study'))),
                ('image_two', models.FileField(blank=True, null=True, upload_to=core.helpers.PathAndRename(sub_path='/supplier_case_study'))),
                ('image_three', models.FileField(blank=True, null=True, upload_to=core.helpers.PathAndRename(sub_path='/supplier_case_study'))),
                ('video_one', models.FileField(blank=True, null=True, upload_to=core.helpers.PathAndRename(sub_path='/supplier_case_study'))),
                ('testimonial', models.CharField(blank=True, default='', max_length=1000, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='companycasestudy',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supplier_case_studies', to='company.Company'),
        ),
    ]
