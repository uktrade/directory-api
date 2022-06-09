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
            sum(imports) AS imports,
            sum(exports) AS exports
        FROM (
            SELECT
                ons_iso_alpha_2_code,
                period,
                CASE WHEN direction = 'imports' THEN
                    value
                END AS imports,
                CASE WHEN direction = 'exports' THEN
                    value
                END AS exports
            FROM
                ons.trade__uk_totals_sa
            WHERE
                period_type = 'quarter'
                AND product_name = 'goods-and-services'
                AND ons_iso_alpha_2_code <> 'Country Code') s
        GROUP BY
            ons_iso_alpha_2_code,
            period;
    '''

    def handle(self, *args, **options):
        data = []
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=5000)

        for chunk in chunks:
            for _idx, row in chunk.iterrows():
                try:
                    country = Country.objects.get(iso2=row.ons_iso_alpha_2_code)
                except Country.DoesNotExist:
                    country = None

                year, quarter = row.period.split('-Q')
                imports = None if row.imports < 0 else row.imports
                exports = None if row.exports < 0 else row.exports

                data.append(
                    UKTotalTradeByCountry(
                        country=country,
                        ons_iso_alpha_2_code=row.ons_iso_alpha_2_code,
                        year=year,
                        quarter=quarter,
                        imports=imports,
                        exports=exports,
                    )
                )
        UKTotalTradeByCountry.objects.all().delete()
        UKTotalTradeByCountry.objects.bulk_create(data)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
