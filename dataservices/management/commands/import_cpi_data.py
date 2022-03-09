import csv
import re

from django.core.management import BaseCommand
from django.db import connection

from dataservices.models import CorruptionPerceptionsIndex


class Command(BaseCommand):
    help = 'Import CorruptionPerceptionsIndex data from transparency.org/'

    def handle(self, *args, **options):

        key_mapping = {'CPI score': 'cpi_score', 'Rank': 'rank'}

        with open('dataservices/resources/corruption_perception_index.csv', 'r', encoding='utf-8-sig') as f:
            file_reader = csv.DictReader(f)
            for row in file_reader:
                store = {}
                country = {'country_name': row.get('Country'), 'country_code': row.get('ISO3')}
                for col_name, value in row.items():
                    # Gather data for several years
                    match = re.match('([^\\d]*)\\s(\\d{4})\\s*$', col_name)
                    if match and value:
                        year = match.group(2)
                        key = match.group(1)
                        if key_mapping.get(key):
                            store[year] = store.get(year) or {}
                            store[year][key_mapping.get(key)] = value
                for out_year, data in store.items():
                    if data.get('rank'):
                        cpi = CorruptionPerceptionsIndex.objects.create(
                            year=out_year,
                            **country,
                            **data,
                        )
                        cpi.save()

            self.stdout.write('Linking countries')
            cursor = connection.cursor()
            cursor.execute(
                "update dataservices_corruptionperceptionsindex as d \
                set country_id=c.id \
                from dataservices_country c where d.country_code=c.iso3;"
            )

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
