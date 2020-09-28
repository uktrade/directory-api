from django.core.management import BaseCommand
from dataservices import models
from directory_constants import choices

class Command(BaseCommand):
    help = 'report country data lookups'

    def handle(self, *args, **options):
        countries = [choice['name'] for choice in choices.COUNTRIES_AND_TERRITORIES_REGION if choice['type'] == 'Country']
        cpi_failed = 0
        cpi_pass = 0
        iu_failed = 0
        iu_pass = 0
        for country in countries:
            if country == 'Congo':
                import pdb
                pdb.set_trace()
            mapped_country = self.map_country_data(country)
            try:
                models.ConsumerPriceIndex.objects.get(country_name=mapped_country)
                cpi_pass = cpi_pass + 1
            except models.ConsumerPriceIndex.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'no cpi data lookup: {country}'))
                cpi_failed = cpi_failed + 1
            try:
                models.InternetUsage.objects.get(country_name=mapped_country)
                iu_pass = iu_pass + 1
            except models.InternetUsage.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'no internet usage data lookup: {country}'))
                iu_failed = iu_failed + 1

        self.stdout.write(self.style.SUCCESS(f'cpi_pass: {cpi_pass}'))
        self.stdout.write(self.style.ERROR(f'cpi_failed: {cpi_failed}'))
        self.stdout.write(self.style.SUCCESS(f'iu_pass: {iu_pass}'))
        self.stdout.write(self.style.ERROR(f'iu_failed: {iu_failed}'))

    def map_country_data(self, country):
        country_map = {
            'Brunei': 'Brunei Darussalam',
            'Congo': 'Congo, Rep.',
            'Congo (Democratic Republic)': 'Congo, Dem. Rep.',
            'Dominican': 'Dominican Republic',
            'Egypt': 'Egypt, Arab Rep.',
            'Micronesia': 'Micronesia, Fed. Sts.',
            'Myanmar (Burma)': 'Myanmar',
            'St Kitts and Nevis': 'St. Kitts and Nevis',
            'St Lucia':  'St. Lucia',
            'St Vincent': 'St. Vincent and the Grenadines',
            'Russia': 'Russian Federation',
            'Syria': 'Syrian Arab Republic',
            'The Bahamas': 'Bahamas, The',
            'The Gambia': 'Gambia, The',
            'Yemen': 'Yemen, Rep.',
            'Venezuela': 'Venezuela, RB',
        }
        return country_map.get(country) if country_map.get(country) is not None else country