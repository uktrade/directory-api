import pandas as pd
import sqlalchemy as sa
from django.conf import settings
from django.core.management import BaseCommand

from dataservices.models import Country, UKTradeInGoodsByCountry


class Command(BaseCommand):
    help = 'Import ONS UK trade in goods data by country from Data Workspace'

    engine = sa.create_engine(settings.DATA_WORKSPACE_DATASETS_URL, execution_options={'stream_results': True})
    sql = '''
        SELECT
            ons_iso_alpha_2_code, period, direction, product_code, product_name, value
        FROM
            ons.trade__uk_goods_nsa
        WHERE
            period_type = 'quarter'
            AND product_code NOT IN('0', '1', '2', '3', '33', '3OF', '4', '5', '6', '7', '78', '79',
            '792/3', '7E', '7EI', '7EK', '7M', '7MC', '7MI', '7MK', '8', '8O', '8OC', 'T');
    '''

    def handle(self, *args, **options):
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=10000)

        UKTradeInGoodsByCountry.objects.all().delete()

        for chunk in chunks:
            for _idx, row in chunk.iterrows():
                try:
                    country = Country.objects.get(iso2=row.ons_iso_alpha_2_code)
                except Country.DoesNotExist:
                    continue

                year, quarter = row.period.replace('quarter/', '').split('-Q')
                value = None if row.value != row.value else row.value

                UKTradeInGoodsByCountry.objects.update_or_create(
                    country=country,
                    year=year,
                    quarter=quarter,
                    commodity_code=row.product_code,
                    commodity_name=row.product_name,
                    defaults={row.direction: value},
                )

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
