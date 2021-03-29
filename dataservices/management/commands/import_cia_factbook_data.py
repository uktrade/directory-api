import requests
from django.core.management import BaseCommand

from dataservices.models import CIAFactbook, Country

name_map = {
    'Bahamas, The': 'The Bahamas',
    'Congo, Republic Of The': 'Congo',
    'Congo, Democratic Republic Of The': 'Congo (Democratic Republic)',
    'Cabo Verde': 'Cape Verde',
    'Cote D\'Ivoire': 'Ivory Coast',
    'Gambia, The': 'The Gambia',
    'Holy See (Vatican City)': 'Vatican City',
    'Korea, South': 'South Korea',
    'Korea, North': 'North Korea',
    'Micronesia, Federated States Of': 'Micronesia',
    'Saint Kitts And Nevis': 'St Kitts and Nevis',
    'Saint Lucia': 'St Lucia',
    'Saint Vincent And The Grenadines': 'St Vincent',
    'Timor-Leste': 'East Timor',
}


class Command(BaseCommand):
    help = 'Import Factbook data'

    def handle(self, *args, **options):
        response = requests.get(
            'https://raw.githubusercontent.com/iancoleman/cia_world_factbook_api/master/data/factbook.json'
        )
        data = response.json()
        CIAFactbook.objects.all().delete()
        for country in data['countries']:
            country_name = data['countries'][country]['data']['name']
            country_ref = None
            lookup_name = name_map.get(country_name, country_name)
            match = Country.objects.filter(name=lookup_name)
            if len(match) == 1:
                country_ref = match[0]
            else:
                match = Country.objects.filter(name__icontains=lookup_name)
                if len(match) == 1:
                    country_ref = match[0]

            country_data = data['countries'][country]['data']

            CIAFactbook(
                country_key=country, country=country_ref, country_name=country_name, factbook_data=country_data
            ).save()

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
