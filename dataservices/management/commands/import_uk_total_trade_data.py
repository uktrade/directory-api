import pandas as pd
import sqlalchemy as sa

from dataservices.models import Country, UKTotalTradeByCountry

from .helpers import MarketGuidesDataIngestionCommand


class Command(MarketGuidesDataIngestionCommand):
    help = 'Import ONS UK total trade data by country from Data Workspace'

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

    def load_data(self):
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

        return data
