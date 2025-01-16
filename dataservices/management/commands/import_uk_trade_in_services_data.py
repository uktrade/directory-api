import json
import logging

import sqlalchemy as sa
from django.conf import settings

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import BaseS3IngestionCommand, ingest_data

logger = logging.getLogger(__name__)

LIVE_TABLE = 'dataservices_uktradeinservicesbycountry'
TEMP_TABLE = 'dataflow_trade_uk_services_nsa_tmp'


class Command(BaseS3IngestionCommand, S3DownloadMixin):
    help = 'Import ONS UK trade in services data by country from Data Workspace'

    def get_temp_batch(self, data, data_table):
        def get_table_data():
            for uk_trade_in_services in data:
                json_data = json.loads(uk_trade_in_services)

                if json_data['product_code'] in ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'):
                    continue

                yield (
                    (
                        data_table,
                        (
                            json_data['ons_iso_alpha_2_code'],
                            json_data['period'],
                            json_data['period_type'],
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
            for uk_trade_in_services in data:
                yield (
                    (
                        data_table,
                        (
                            uk_trade_in_services['country_id'],
                            uk_trade_in_services['period'],
                            uk_trade_in_services['period_type'],
                            uk_trade_in_services['service_code'],
                            uk_trade_in_services['service_name'],
                            uk_trade_in_services['imports'],
                            uk_trade_in_services['exports'],
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
            sa.Column("period_type", sa.TEXT, nullable=False),
            sa.Column("product_code", sa.TEXT, nullable=False),
            sa.Column("product_name", sa.TEXT, nullable=False),
            sa.Column("direction", sa.TEXT, nullable=False),
            sa.Column("value", sa.DECIMAL(10, 2), nullable=True),
            sa.Index(None, "ons_iso_alpha_2_code"),
            sa.Index(None, "period"),
            sa.Index(None, "period_type"),
            sa.Index(None, "product_code"),
            sa.Index(None, "product_name"),
            sa.Index(None, "direction"),
            sa.Index(None, "ons_iso_alpha_2_code", "period", "period_type", "product_code", "direction"),
            schema="public",
        )

    def get_postgres_table(self):
        return sa.Table(
            LIVE_TABLE,
            self.metadata,
            sa.Column("country_id", sa.INTEGER, nullable=True),
            sa.Column("period", sa.TEXT, nullable=False),
            sa.Column("period_type", sa.TEXT, nullable=False),
            sa.Column("service_code", sa.TEXT, nullable=True),
            sa.Column("service_name", sa.TEXT, nullable=True),
            sa.Column("imports", sa.DECIMAL(10, 2), nullable=True),
            sa.Column("exports", sa.DECIMAL(10, 2), nullable=True),
            schema="public",
            keep_existing=True,
        )

    def load_data(self, delete_temp_tables=True, *args, **options):
        try:
            data = self.do_handle(prefix=settings.TRADE_UK_SERVICES_NSA_FROM_S3_PREFIX)
            self.save_temp_data(data)
            self.save_import_data([])
        except Exception:
            logger.exception("import_uk_trade_in_services_data failed to ingest data from s3")
        finally:
            if delete_temp_tables:
                self.delete_temp_tables([TEMP_TABLE])

    def save_import_data(self, data):
        sql = f'''
            SELECT
                iso2,
                period,
                period_type,
                service_code,
                service_name,
                sum(imports) AS imports,
                sum(exports) AS exports,
                country_id
            FROM (
                SELECT
                    dataservices_country.id AS country_id,
                    ons_iso_alpha_2_code AS iso2,
                    period,
                    period_type,
                    product_code AS service_code,
                    product_name AS service_name,
                    CASE WHEN direction = 'imports' THEN
                        value
                    END AS imports,
                    CASE WHEN direction = 'exports' THEN
                        value
                    END AS exports
                FROM
                    {TEMP_TABLE}
                    LEFT JOIN dataservices_country ON {TEMP_TABLE}.ons_iso_alpha_2_code = dataservices_country.iso2) s
            GROUP BY
                iso2,
                period,
                period_type,
                service_code,
                service_name,
                country_id;
        '''

        with self.engine.connect() as connection:
            cnt = 0

            batch = connection.execute(sa.text(sql))

            for row in batch:
                imports = None if not row.imports else float(row.imports)
                exports = None if not row.exports else float(row.exports)

                data.append(
                    {
                        'period': row.period,
                        'period_type': row.period_type,
                        'service_code': row.service_code,
                        'service_name': row.service_name,
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
