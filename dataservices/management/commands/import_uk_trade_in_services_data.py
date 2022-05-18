import pandas as pd
import sqlalchemy as sa
from django.conf import settings
from django.core.management import BaseCommand

from dataservices.models import Country, UKTradeInServiceByCountry


class Command(BaseCommand):
    help = 'Import ONS UK trade in services data by country from Data Workspace'

    engine = sa.create_engine(settings.DATA_WORKSPACE_DATASETS_URL, execution_options={'stream_results': True})
    sql = '''
        SELECT
            ons_iso_alpha_2_code, period, direction, product_code, product_name, value
        FROM
            ons.trade__uk_services_nsa
        WHERE
            period_type = 'quarter'
            AND product_code IN('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12');
    '''

    def handle(self, *args, **options):
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=5000)

        UKTradeInServiceByCountry.objects.all().delete()

        for chunk in chunks:
            for _idx, row in chunk.iterrows():
                try:
                    country = Country.objects.get(iso2=row.ons_iso_alpha_2_code)
                except Country.DoesNotExist:
                    continue

                year, quarter = row.period.replace('quarter/', '').split('-Q')
                value = None if row.value != row.value else row.value

                UKTradeInServiceByCountry.objects.update_or_create(
                    country=country,
                    year=year,
                    quarter=quarter,
                    service_code=row.product_code,
                    service_name=row.product_name,
                    defaults={row.direction: value},
                )

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
