import pandas as pd
import sqlalchemy as sa

from dataservices.models import Country, UKTradeInGoodsByCountry

from .helpers import MarketGuidesDataIngestionCommand


class Command(MarketGuidesDataIngestionCommand):
    help = 'Import ONS UK trade in goods data by country from Data Workspace'

    sql = '''
        SELECT
            iso2,
            period,
            commodity_code,
            commodity_name,
            sum(imports) AS imports,
            sum(exports) AS exports
        FROM (
            SELECT
                ons_iso_alpha_2_code AS iso2,
                period,
                product_code AS commodity_code,
                product_name AS commodity_name,
                CASE WHEN direction = 'imports' THEN
                    value
                END AS imports,
                CASE WHEN direction = 'exports' THEN
                    value
                END AS exports
            FROM
                ons.trade__uk_goods_nsa
            WHERE
                period_type = 'quarter'
                AND product_code NOT IN('0', '1', '2', '3', '33', '3OF', '4', '5', '6', '7', '78', '79',
                '792/3', '7E', '7EI', '7EK', '7M', '7MC', '7MI', '7MK', '8', '8O', '8OC', 'T')) s
        GROUP BY
            iso2,
            period,
            commodity_code,
            commodity_name;
    '''

    def load_data(self):
        data = []
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=5000)

        for chunk in chunks:
            for _idx, row in chunk.iterrows():
                try:
                    country = Country.objects.get(iso2=row.iso2)
                except Country.DoesNotExist:
                    continue

                year, quarter = row.period.replace('quarter/', '').split('-Q')
                imports = None if row.imports != row.imports else row.imports
                exports = None if row.exports != row.exports else row.exports

                data.append(
                    UKTradeInGoodsByCountry(
                        country=country,
                        year=year,
                        quarter=quarter,
                        commodity_code=row.commodity_code,
                        commodity_name=row.commodity_name,
                        imports=imports,
                        exports=exports,
                    )
                )

        return data
