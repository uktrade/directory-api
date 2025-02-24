import json
import logging

import sqlalchemy as sa
from django.conf import settings

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import BaseS3IngestionCommand, ingest_data

logger = logging.getLogger(__name__)

LIVE_TABLE = 'dataservices_uktradeingoodsbycountry'
TEMP_TABLE = 'dataflow_trade_uk_goods_nsa_tmp'


class Command(BaseS3IngestionCommand, S3DownloadMixin):
    help = help = 'Import ONS UK trade in goods data by country from s3'

    def get_temp_batch(self, data, data_table):
        def get_table_data():
            for uk_trade_in_goods in data:
                json_data = json.loads(uk_trade_in_goods)

                yield (
                    (
                        data_table,
                        (
                            json_data['ons_iso_alpha_2_code'],
                            json_data['period'],
                            json_data['product_code'],
                            json_data['product_name'],
                            json_data['direction'],
                            json_data['value'],
                        ),
                    )
                )

        return (
            None,
            None,
            get_table_data(),
        )

    def get_batch(self, data, data_table):
        def get_table_data():
            for uk_trade_in_goods in data:
                yield (
                    (
                        data_table,
                        (
                            uk_trade_in_goods['country_id'],
                            uk_trade_in_goods['year'],
                            uk_trade_in_goods['quarter'],
                            uk_trade_in_goods['commodity_code'],
                            uk_trade_in_goods['commodity_name'],
                            uk_trade_in_goods['imports'],
                            uk_trade_in_goods['exports'],
                        ),
                    )
                )

        return (
            None,
            None,
            get_table_data(),
        )

    def get_temp_postgres_table(self):
        return sa.Table(
            TEMP_TABLE,
            self.metadata,
            sa.Column("ons_iso_alpha_2_code", sa.TEXT, nullable=False),
            sa.Column("period", sa.TEXT, nullable=False),
            sa.Column("product_code", sa.TEXT, nullable=False),
            sa.Column("product_name", sa.TEXT, nullable=False),
            sa.Column("direction", sa.TEXT, nullable=False),
            sa.Column("value", sa.DECIMAL(10, 2), nullable=True),
            sa.Index(None, "ons_iso_alpha_2_code"),
            sa.Index(None, "period"),
            sa.Index(None, "product_code"),
            sa.Index(None, "product_name"),
            sa.Index(None, "direction"),
            sa.Index(None, "ons_iso_alpha_2_code", "period", "product_code", "product_name", "direction"),
            schema="public",
        )

    def get_postgres_table(self):
        return sa.Table(
            LIVE_TABLE,
            self.metadata,
            sa.Column("country_id", sa.INTEGER, nullable=True),
            sa.Column("year", sa.INTEGER, nullable=False),
            sa.Column("quarter", sa.SMALLINT, nullable=False),
            sa.Column("commodity_code", sa.TEXT, nullable=True),
            sa.Column("commodity_name", sa.TEXT, nullable=False),
            sa.Column("imports", sa.DECIMAL(10, 2), nullable=True),
            sa.Column("exports", sa.DECIMAL(10, 2), nullable=True),
            schema="public",
            keep_existing=True,
        )

    def load_data(self, delete_temp_tables=True, *args, **options):
        try:
            data = self.do_handle(prefix=settings.TRADE_UK_GOODS_NSA_FROM_S3_PREFIX)
            self.save_temp_data(data)
            self.save_import_data([])
        except Exception:
            logger.exception("import_uk_trade_in_goods_data failed to ingest data from s3")
        finally:
            if delete_temp_tables:
                self.delete_temp_tables([TEMP_TABLE])

    def save_import_data(self, data):
        sql = f'''
            SELECT
                iso2,
                period,
                commodity_code,
                commodity_name,
                sum(imports) AS imports,
                sum(exports) AS exports,
                country_id
            FROM
                (
                    SELECT
                        dataservices_country.id AS country_id,
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
                        {TEMP_TABLE}
                        LEFT JOIN dataservices_country ON {TEMP_TABLE}.ons_iso_alpha_2_code = dataservices_country.iso2
                ) s
            GROUP BY
                iso2,
                period,
                commodity_code,
                commodity_name,
                country_id;
        '''

        with self.engine.connect() as connection:
            cnt = 0

            batch = connection.execute(sa.text(sql))

            for row in batch:
                year, quarter = row.period.replace('quarter/', '').split('-Q')
                imports = None if not row.imports else float(row.imports)
                exports = None if not row.exports else float(row.exports)

                data.append(
                    {
                        'year': year,
                        'quarter': quarter,
                        'commodity_code': row.commodity_code,
                        'commodity_name': row.commodity_name,
                        'imports': imports,
                        'exports': exports,
                        'country_id': row.country_id,
                    }
                )

                cnt += 1
                if (cnt % 100000) == 0:
                    logger.info(f'Processing record {cnt}')

        data_table = self.get_postgres_table()

        def on_before_visible(conn, ingest_table, batch_metadata):
            pass

        def batches(_):
            yield self.get_batch(data, data_table)

        ingest_data(self.engine, self.metadata, on_before_visible, batches)
