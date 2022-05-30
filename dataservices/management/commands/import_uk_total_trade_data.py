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
            ons_iso_alpha_2_code, period, direction, value
        FROM
            ons.trade__uk_totals_sa
        WHERE
            period_type = 'quarter'
            AND product_name = 'goods-and-services';
    '''

    def handle(self, *args, **options):
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=5000)

        UKTotalTradeByCountry.objects.all().delete()

        for chunk in chunks:
            for _idx, row in chunk.iterrows():
                try:
                    country = Country.objects.get(iso2=row.ons_iso_alpha_2_code)
                except Country.DoesNotExist:
                    # We need to store rows for 'World Total' (iso2 'W1')
                    if row.ons_iso_alpha_2_code == 'W1':
                        country = None
                    else:
                        continue

                year, quarter = row.period.split('-Q')
                value = None if row.value < 0 else row.value

                UKTotalTradeByCountry.objects.update_or_create(
                    country=country,
                    year=year,
                    quarter=quarter,
                    defaults={row.direction: value},
                )

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
