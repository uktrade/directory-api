import json
import logging
import random
import time

import sqlalchemy as sa
from django.conf import settings

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import BaseS3IngestionCommand

logger = logging.getLogger(__name__)

LIVE_TABLE = 'dataservices_uktradeingoodsbycountry'
TEMP_TABLE = 'dataflow_trade_uk_goods_nsa_tmp'


class Command(BaseS3IngestionCommand, S3DownloadMixin):
    help = 'Import ONS UK trade in goods data by country from s3'

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

        return (None, None, get_table_data())

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

    def load_data(self, delete_temp_tables=True, *args, **options):
        try:
            data = self.do_handle(prefix=settings.TRADE_UK_GOODS_NSA_FROM_S3_PREFIX)
            self.save_temp_data(data)
            self.save_import_data()
        except Exception:
            logger.exception("import_uk_trade_in_goods_data failed to ingest data from s3")
        finally:
            if delete_temp_tables:
                self.delete_temp_tables([TEMP_TABLE])

    def save_import_data(self):
        """Direct SQL approach for better performance"""
        MAX_RETRIES = 5
        QUERY_TIMEOUT = 120  # seconds

        # SQL for direct insert from temp table to live table
        direct_sql = f"""
            INSERT INTO {LIVE_TABLE}
            (country_id, year, quarter, commodity_code, commodity_name, imports, exports)
            SELECT
                c.id as country_id,
                CAST(SPLIT_PART(REPLACE(t.period, 'quarter/', ''), '-Q', 1) AS INTEGER) as year,
                CAST(SPLIT_PART(REPLACE(t.period, 'quarter/', ''), '-Q', 2) AS SMALLINT) as quarter,
                t.product_code as commodity_code,
                t.product_name as commodity_name,
                CASE WHEN SUM(CASE WHEN t.direction = 'imports' THEN t.value ELSE 0 END) > 0
                     THEN SUM(CASE WHEN t.direction = 'imports' THEN t.value ELSE 0 END)
                     ELSE NULL
                END as imports,
                CASE WHEN SUM(CASE WHEN t.direction = 'exports' THEN t.value ELSE 0 END) > 0
                     THEN SUM(CASE WHEN t.direction = 'exports' THEN t.value ELSE 0 END)
                     ELSE NULL
                END as exports
            FROM {TEMP_TABLE} t
            LEFT JOIN dataservices_country c ON t.ons_iso_alpha_2_code = c.iso2
            GROUP BY
                c.id,
                t.period,
                t.product_code,
                t.product_name
        """

        # Truncate and insert with retry logic
        for attempt in range(MAX_RETRIES):
            try:
                with self.engine.connect() as connection:
                    # Truncate the target table
                    logger.info(f"Truncating and repopulating {LIVE_TABLE}")
                    connection.execute(sa.text(f"TRUNCATE TABLE {LIVE_TABLE}"))

                    # Set timeout and execute insert
                    connection.execute(sa.text(f"SET statement_timeout = {QUERY_TIMEOUT * 1000}"))
                    result = connection.execute(sa.text(direct_sql))
                    connection.commit()

                    # Log success
                    logger.info(f"Successfully inserted {result.rowcount} records")
                    return

            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    sleep_time = (2**attempt) + random.uniform(0, 1)
                    logger.warning(
                        f"Error, retrying in {sleep_time:.2f}s (attempt {attempt+1}/{MAX_RETRIES}): {str(e)}"
                    )
                    time.sleep(sleep_time)
                else:
                    logger.error(f"Failed after {MAX_RETRIES} attempts: {str(e)}")
                    raise
