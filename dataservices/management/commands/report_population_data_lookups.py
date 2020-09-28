from django.core.management import BaseCommand
from directory_constants import choices
from dataservices import helpers


class Command(BaseCommand):
    help = 'report population data lookups'

    def handle(self, *args, **options):
        countries = [
            choice['name'] for choice in choices.COUNTRIES_AND_TERRITORIES_REGION if choice['type'] == 'Country'
        ]
        population_pass = 0
        population_failed = 0
        for country in countries:
            population_data = helpers.PopulationData().get_population_total_data(country)
            if population_data.get('total_population'):
                population_pass = population_pass + 1
            else:
                population_failed = population_failed + 1
                self.stdout.write(self.style.ERROR(f'no population data for lookup: {country}'))

        self.stdout.write(self.style.SUCCESS(f'population_pass: {population_pass}'))
        self.stdout.write(self.style.ERROR(f'population_failed: {population_failed}'))
