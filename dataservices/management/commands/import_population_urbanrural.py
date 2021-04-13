import csv

from django.core.management import BaseCommand

from dataservices.models import Country, PopulationUrbanRural


class Command(BaseCommand):
    help = 'Import population urban versus rural'

    import_years = ['2018', '2019', '2020', '2021', '2022', '2023', '2024']

    def handle(self, *args, **options):
        population_data = []

        for urban_rural in ['urban', 'rural']:
            with open(f'dataservices/resources/{urban_rural}_population_annual.csv', 'r', encoding='utf-8-sig') as f:
                file_reader = csv.DictReader(f)

                for row in file_reader:
                    try:
                        country = Country.objects.get(iso1=row['country_code'].zfill(3))
                    except Country.DoesNotExist:
                        country = None
                        self.stdout.write(f'No country match for {row["country_name"]}')
                    for year in self.import_years:
                        value = row.get(year)
                        if value:
                            population_data.append(
                                PopulationUrbanRural(country=country, year=year, urban_rural=urban_rural, value=value)
                            )

            PopulationUrbanRural.objects.all().delete()
            PopulationUrbanRural.objects.bulk_create(population_data)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
