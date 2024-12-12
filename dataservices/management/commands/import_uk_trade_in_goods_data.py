import json
import logging

import pandas as pd
import sqlalchemy as sa
from django.conf import settings
from django.core.management.base import BaseCommand

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import ingest_data
from dataservices.models import Country

logger = logging.getLogger(__name__)


def get_uk_trade_in_goods_tmp_batch(data, data_table):

    def get_table_data():

        for uk_trade_in_goods in data:
            json_data = json.loads(uk_trade_in_goods)

            if json_data['period_type'] != 'quarter':
                continue

            if json_data['product_code'] in (
                '0',
                '1',
                '2',
                '3',
                '33',
                '3OF',
                '4',
                '5',
                '6',
                '7',
                '78',
                '79',
                '792/3',
                '7E',
                '7EI',
                '7EK',
                '7M',
                '7MC',
                '7MI',
                '7MK',
                '8',
                '8O',
                '8OC',
                'T',
            ):
                continue

            imports = None
            exports = None

            if json_data['direction'] == 'imports':
                imports = json_data['value']
            else:
                exports = json_data['value']

            yield (
                (
                    data_table,
                    (
                        json_data['ons_iso_alpha_2_code'],
                        json_data['period'],
                        json_data['product_code'],
                        json_data['product_name'],
                        imports,
                        exports,
                    ),
                )
            )

    return (
        None,
        None,
        get_table_data(),
    )


def get_uk_trade_in_goods_tmp_postgres_table(metadata):
    return sa.Table(
        "dataservices_tmp_uktradeingoodsbycountry",
        metadata,
        sa.Column("ons_iso_alpha_2_code", sa.TEXT, nullable=False),
        sa.Column("period", sa.TEXT, nullable=False),
        sa.Column("product_code", sa.TEXT, nullable=True),
        sa.Column("product_name", sa.TEXT, nullable=False),
        sa.Column("imports", sa.DECIMAL(10, 2), nullable=True),
        sa.Column("exports", sa.DECIMAL(10, 2), nullable=True),
        schema="public",
    )


def get_uk_trade_in_goods_postgres_table(metadata):
    return sa.Table(
        "dataservices_uktradeingoodsbycountry",
        metadata,
        sa.Column("country_id", sa.INTEGER, nullable=False),
        sa.Column("year", sa.INTEGER, nullable=False),
        sa.Column("quarter", sa.SMALLINT, nullable=False),
        sa.Column("commodity_code", sa.TEXT, nullable=True),
        sa.Column("commodity_name", sa.TEXT, nullable=False),
        sa.Column("imports", sa.DECIMAL(10, 2), nullable=True),
        sa.Column("exports", sa.DECIMAL(10, 2), nullable=True),
        schema="public",
    )


def get_uk_trade_in_goods_batch(data, data_table):

    def get_table_data():

        for uk_trade_in_goods in data:
            json_data = json.loads(uk_trade_in_goods)

            yield (
                (
                    data_table,
                    (
                        json_data['year'],
                        json_data['quarter'],
                        json_data['commodity_code'],
                        json_data['commodity_name'],
                        json_data['imports'],
                        json_data['exports'],
                    ),
                )
            )

    return (
        None,
        None,
        get_table_data(),
    )


def save_uk_trade_in_goods_tmp_data(data):

    engine = sa.create_engine(settings.DATABASE_URL, future=True)

    metadata = sa.MetaData()

    data_table = get_uk_trade_in_goods_tmp_postgres_table(metadata)

    def on_before_visible(conn, ingest_table, batch_metadata):
        pass

    def batches(_):
        yield get_uk_trade_in_goods_tmp_batch(data, data_table)

    ingest_data(engine, metadata, on_before_visible, batches)


def save_uk_trade_in_goods_data():
    breakpoint()
    engine = sa.create_engine(settings.DATABASE_URL, future=True)
    data = []

    sql = '''
        SELECT
            ons_iso_alpha_2_code AS iso2,
            period,
            product_code AS commodity_code,
            product_name AS commodity_name,
            sum(imports) AS imports,
            sum(exports) AS exports
        FROM public.dataservices_tmp_uktradeingoodsbycountry
        GROUP BY
            iso2,
            period,
            commodity_code,
            commodity_name;
    '''

    with engine.connect() as connection:
        chunks = pd.read_sql_query(sa.text(sql), connection, chunksize=10000)

        for chunk in chunks:
            for _, row in chunk.iterrows():

                try:
                    country = Country.objects.get(iso2=row.iso2)
                except Country.DoesNotExist:
                    continue

                year, quarter = row.period.replace('quarter/', '').split('-Q')
                imports = None if row.imports != row.imports else row.imports
                exports = None if row.exports != row.exports else row.exports

                data.append(
                    {
                        'year': year,
                        'quarter': quarter,
                        'commodity_code': row.commodity_code,
                        'commodity_name': row.commodity_name,
                        'imports': imports,
                        'exports': exports,
                        'country_id': country.id,
                    }
                )

    breakpoint()
    metadata = sa.MetaData()

    data_table = get_uk_trade_in_goods_postgres_table(metadata, 'dataservices_eybbusinessclusterinformation')

    def on_before_visible(conn, ingest_table, batch_metadata):
        pass

    def batches(_):
        yield get_uk_trade_in_goods_batch(data, data_table)

    ingest_data(engine, metadata, on_before_visible, batches)


class Command(BaseCommand, S3DownloadMixin):

    help = help = 'Import ONS UK trade in goods data by country from s3'

    def handle(self, *args, **options):
        try:
            self.do_handle(
                prefix=settings.TRADE_UK_GOODS_NSA_FROM_S3_PREFIX,
                save_func=save_uk_trade_in_goods_tmp_data,
            )
            save_uk_trade_in_goods_data()
        except Exception:
            logger.exception("import_uk_trade_in_goods_data failed to ingest data from s3")
        finally:
            self.delete_temp_tables(
                [
                    'dataservices_tmp_uktradeingoodsbycountry',
                ]
            )


# class Command(MarketGuidesDataIngestionCommand):
#     help = 'Import ONS UK trade in goods data by country from Data Workspace'

#     sql = '''
#         SELECT
#             iso2,
#             period,
#             commodity_code,
#             commodity_name,
#             sum(imports) AS imports,
#             sum(exports) AS exports
#         FROM (
#             SELECT
#                 ons_iso_alpha_2_code AS iso2,
#                 period,
#                 product_code AS commodity_code,
#                 product_name AS commodity_name,
#                 CASE WHEN direction = 'imports' THEN
#                     value
#                 END AS imports,
#                 CASE WHEN direction = 'exports' THEN
#                     value
#                 END AS exports
#             FROM
#                 ons.trade__uk_goods_nsa
#             WHERE
#                 period_type = 'quarter'
#                 AND product_code NOT IN('0', '1', '2', '3', '33', '3OF', '4', '5', '6', '7', '78', '79',
#                 '792/3', '7E', '7EI', '7EK', '7M', '7MC', '7MI', '7MK', '8', '8O', '8OC', 'T')) s
#         GROUP BY
#             iso2,
#             period,
#             commodity_code,
#             commodity_name;
#     '''

#     def load_data(self):
#         data = []
#         chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=10000)

#         for chunk in chunks:
#             for _idx, row in chunk.iterrows():
#                 try:
#                     country = Country.objects.get(iso2=row.iso2)
#                 except Country.DoesNotExist:
#                     continue

#                 year, quarter = row.period.replace('quarter/', '').split('-Q')
#                 imports = None if row.imports != row.imports else row.imports
#                 exports = None if row.exports != row.exports else row.exports

#                 data.append(
#                     UKTradeInGoodsByCountry(
#                         country=country,
#                         year=year,
#                         quarter=quarter,
#                         commodity_code=row.commodity_code,
#                         commodity_name=row.commodity_name,
#                         imports=imports,
#                         exports=exports,
#                     )
#                 )

#         return data
