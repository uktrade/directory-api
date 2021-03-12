import tablib
from django.core.management import BaseCommand
from django.db import connection
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
            GDPPerCapita.objects.all().delete()
            gdp_per_capita_resource.import_data(dataset, dry_run=False)

            self.stdout.write('Linking countries')
            cursor = connection.cursor()
            cursor.execute(
                "update dataservices_gdppercapita as d \
                set country_id=c.id \
                from dataservices_country c where d.country_code=c.iso3;"
            )
        self.stdout.write(self.style.SUCCESS('All done, bye!'))
