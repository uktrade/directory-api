from django.apps import apps
from django.core.management import BaseCommand

from conf import settings
from dataservices.models import Country

from .helpers import flatten_ordered_dict, from_url_get_xml


class Command(BaseCommand):
    help = 'Import data from world bank'

    loader_info = {
        'consumerpriceindex': {
            'url': f'{settings.WORLD_BANK_API_URI}FP.CPI.TOTL.ZG?downloadformat=xml',
            'model_name': 'ConsumerPriceIndex',
        },
        'gdpcapita': {
            'url': f'{settings.WORLD_BANK_API_URI}NY.GDP.PCAP.CD?downloadformat=xml',
            'model_name': 'GDPPerCapita',
        },
        'easeofdoingbusiness': {
            'url': f'{settings.WORLD_BANK_API_URI}IC.BUS.EASE.XQ?downloadformat=xml',
            'model_name': 'EaseOfDoingBusiness',
        },
        'income': {
            'url': f'{settings.WORLD_BANK_API_URI}/NY.ADJ.NNTY.PC.CD?downloadformat=xml',
            'model_name': 'Income',
        },
        'internetusage': {
            'url': f'{settings.WORLD_BANK_API_URI}/IT.NET.USER.ZS?downloadformat=xml',
            'model_name': 'InternetUsage',
        },
    }

    def handle(self, *args, **options):
        world_bank_load = options['world_bank_load']
        for load in world_bank_load:
            load = load.lower()
            if load == 'all':
                for load_key in self.loader_info.keys():
                    self.load_worldbank_data(**self.loader_info[load_key])
                return
            if load in self.loader_info.keys():
                self.load_worldbank_data(**self.loader_info[load])
            else:
                self.stdout.write(self.style.ERROR(f'No world bank loader found for: {load}'))

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            'world_bank_load',
            nargs='*',
            type=str,
            default=['all'],
            help=('Specify worldbank loader options : cpi, gdpcapita, easeofdoingbusiness all'),
        )

    def load_worldbank_data(self, url, model_name):

        xml_data = from_url_get_xml(url)
        data_objects = []
        countries_not_found = []
        model = apps.get_model('dataservices', model_name)

        for record in xml_data['Root']['data']['record']:
            record_dict = flatten_ordered_dict(record['field'])
            iso3, _ = record_dict['Country or Area']
            _, year = record_dict['Year']
            _, val = record_dict['Value']

            if iso3 and val and year and iso3 not in countries_not_found:
                existing_record = model.objects.filter(country__iso3=iso3, year=year)
                existing_record.delete()
                try:
                    country = Country.objects.get(iso3=iso3)
                    data_dict = {'year': year, 'value': val, 'country': country}
                    data_objects.append(model(**data_dict))
                except Country.DoesNotExist:
                    countries_not_found.append(iso3)
                    self.stdout.write(self.style.WARNING(f'Country code not found: {iso3}'))

        model.objects.bulk_create(data_objects)
        self.stdout.write(self.style.SUCCESS(f'Added {model_name} Data total records: {len(data_objects)}'))
