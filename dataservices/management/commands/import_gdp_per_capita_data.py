import tablib
from django.core.management import BaseCommand
from import_export import resources

from dataservices.models import GDPPerCapita


class Command(BaseCommand):
    help = 'Import GDP Per Capita data for 2019 from www.imf.org'

    def handle(self, *args, **options):
        with open(
            'dataservices/resources/API_NY.GDP.PCAP.CD_DS2_en_csv_v2_1637514.csv', 'r', encoding='utf-8-sig'
        ) as f:
            data = tablib.import_set(f.read(), format='csv', headers=True)
            dataset = tablib.Dataset(headers=['country_name', 'country_code', 'year_2019'])

            for item in data:
                dataset.append(
                    (
                        item[0],
                        item[1],
                        item[63],
                    )
                )

            gdp_per_capita_resource = resources.modelresource_factory(model=GDPPerCapita)()
            result = gdp_per_capita_resource.import_data(dataset, dry_run=True)
            self.stdout.write(self.style.SUCCESS(result.has_errors()))
            if not result.has_errors():
                # No Errors lets flush table and import the data
                GDPPerCapita.objects.all().delete()
                gdp_per_capita_resource.import_data(dataset, dry_run=False)
        self.stdout.write(self.style.SUCCESS('All done, bye!'))
