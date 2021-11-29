import csv
import glob
import re

import tablib
from django.core.management import BaseCommand
from django.db import connection
from import_export import resources

from dataservices.models import Country, EaseOfDoingBusiness

REG_GET_YEAR = re.compile(r'.*(\d{4})$')


class Command(BaseCommand):
    help = 'Import easeofdoingbusiness data from worldbank.'

    def delete_junk(self):
        EaseOfDoingBusiness.objects.filter(country_code=None).delete()
        EaseOfDoingBusiness.objects.filter(year=None).delete()

    def handle(self, *args, **options):
        self.delete_junk()
        files = glob.glob('dataservices/resources/EaseOfDoingBusiness*.csv', recursive=False)
        for filename in files:
            self.stdout.write(f'Loading from file "{filename}"')
            unknown_countries = 0
            rows_updated = 0
            rows_added = 0
            rows_skipped = 0
            with open(filename, 'r', encoding='utf-8-sig') as f:
                file_reader = csv.DictReader(f)
                for row in file_reader:
                    try:
                        value = int(row.get('Value') or 0)
                        if value:
                            year_match = REG_GET_YEAR.match(row.get('Time Code'))
                            if year_match:
                                year = int(year_match.groups()[0])
                                country_code = row.get('Country Code')
                                country = Country.objects.get(iso3=country_code)
                                entry = EaseOfDoingBusiness.objects.filter(country=country, year=year).first()
                                if not entry:
                                    entry = EaseOfDoingBusiness.objects.create(
                                        country=country, country_code=country_code, year=year, value=value
                                    )
                                    rows_added += 1
                                elif entry.value != value:
                                    entry.value = value
                                    rows_updated += 1
                                else:
                                    rows_skipped += 1
                                entry.save()

                    except Country.DoesNotExist:
                        unknown_countries += 1

            self.stdout.write(f'Unmatched countries: {unknown_countries}')
            self.stdout.write(f'Rows updated       : {rows_updated}')
            self.stdout.write(f'Rows added         : {rows_added}')
            self.stdout.write(f'Rows untouched     : {rows_skipped}')

    def handle_old(self, *args, **options):
        with open('dataservices/resources/EaseOfDoingBusiness.csv', 'r', encoding='utf-8-sig') as f:
            data = tablib.import_set(f.read(), format='csv', headers=True)
            easeofdoingbusiness_resource = resources.modelresource_factory(model=EaseOfDoingBusiness)()
            EaseOfDoingBusiness.objects.all().delete()
            easeofdoingbusiness_resource.import_data(data, dry_run=False)
            self.stdout.write('Linking countries')
            cursor = connection.cursor()
            cursor.execute(
                "update dataservices_easeofdoingbusiness as d \
                set country_id=c.id \
                from dataservices_country c where d.country_code=c.iso3;"
            )
        self.stdout.write(self.style.SUCCESS('All done, bye!'))
