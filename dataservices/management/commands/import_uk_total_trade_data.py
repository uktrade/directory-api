import pandas as pd
import sqlalchemy as sa
from django.conf import settings
from django.core.management import BaseCommand

from dataservices.models import Country, UKTotalTradeByCountry


class Command(BaseCommand):
    help = 'Import ONS UK total trade data by country from Data Workspace'

    engine = sa.create_engine(settings.DATA_WORKSPACE_DATASETS_URL, execution_options={'stream_results': True})
    sql = '''
        SELECT
            ons_iso_alpha_2_code,
            period,
            direction,
            value
        FROM
            ons.trade__uk_totals_sa
        WHERE
            period_type = 'quarter'
            AND product_name = 'goods-and-services'
            -- 	this value sneaked into the source somehow
            AND ons_iso_alpha_2_code <> 'Country Code';
    '''

    def handle(self, *args, **options):
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=5000)

        UKTotalTradeByCountry.objects.all().delete()

        for chunk in chunks:
            for _idx, row in chunk.iterrows():
                try:
                    country = Country.objects.get(iso2=row.ons_iso_alpha_2_code)
                except Country.DoesNotExist:
                    country = None

                year, quarter = row.period.split('-Q')
                value = None if row.value < 0 else row.value

                UKTotalTradeByCountry.objects.update_or_create(
                    country=country,
                    ons_iso_alpha_2_code=row.ons_iso_alpha_2_code,
                    year=year,
                    quarter=quarter,
                    defaults={row.direction: value},
                )

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
