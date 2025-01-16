import json
import logging

import sqlalchemy as sa
from django.conf import settings

from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import BaseS3IngestionCommand, ingest_data
from dataservices.models import Country

logger = logging.getLogger(__name__)

LIVE_TABLE = 'dataservices_worldeconomicoutlookbycountry'
TEMP_TABLE = 'dataflow_world_economic_outlook_by_country_tmp'


class Command(BaseS3IngestionCommand, S3DownloadMixin):
    help = 'Import IMF world economic outlook data by country from Data Workspace'

    def get_temp_batch(self, data, data_table):
        def get_table_data():
            for world_economic_outlook in data:
                json_data = json.loads(world_economic_outlook)

                if not json_data['weo_subject_code'] in ('NGDPD', 'NGDPDPC', 'NGDP_RPCH'):
                    continue

                yield (
                    (
                        data_table,
                        (
                            json_data['iso'],
                            json_data['weo_subject_code'],
                            json_data['subject_descriptor'],
                            json_data['subject_notes'],
                            json_data['units'],
                            json_data['scale'],
                            json_data['estimates_start_after'],
                            json_data['year_1980'],
                            json_data['year_1981'],
                            json_data['year_1982'],
                            json_data['year_1983'],
                            json_data['year_1984'],
                            json_data['year_1985'],
                            json_data['year_1986'],
                            json_data['year_1987'],
                            json_data['year_1988'],
                            json_data['year_1989'],
                            json_data['year_1990'],
                            json_data['year_1991'],
                            json_data['year_1992'],
                            json_data['year_1993'],
                            json_data['year_1994'],
                            json_data['year_1995'],
                            json_data['year_1996'],
                            json_data['year_1997'],
                            json_data['year_1998'],
                            json_data['year_1999'],
                            json_data['year_2000'],
                            json_data['year_2001'],
                            json_data['year_2002'],
                            json_data['year_2003'],
                            json_data['year_2004'],
                            json_data['year_2005'],
                            json_data['year_2006'],
                            json_data['year_2007'],
                            json_data['year_2008'],
                            json_data['year_2009'],
                            json_data['year_2010'],
                            json_data['year_2011'],
                            json_data['year_2012'],
                            json_data['year_2013'],
                            json_data['year_2014'],
                            json_data['year_2015'],
                            json_data['year_2016'],
                            json_data['year_2017'],
                            json_data['year_2018'],
                            json_data['year_2019'],
                            json_data['year_2020'],
                            json_data['year_2021'],
                            json_data['year_2022'],
                            json_data['year_2023'],
                            json_data['year_2024'],
                            json_data['year_2025'],
                            json_data['year_2026'],
                            json_data['year_2027'],
                            json_data['year_2028'],
                            json_data['year_2029'],
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
            for world_economic_outlook in data:
                yield (
                    (
                        data_table,
                        (
                            world_economic_outlook['country_id'],
                            world_economic_outlook['ons_iso_alpha_3_code'],
                            world_economic_outlook['subject_code'],
                            world_economic_outlook['subject_descriptor'],
                            world_economic_outlook['subject_notes'],
                            world_economic_outlook['units'],
                            world_economic_outlook['scale'],
                            world_economic_outlook['year'],
                            world_economic_outlook['value'],
                            world_economic_outlook['estimates_start_after'],
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
            sa.Column("iso", sa.TEXT, nullable=False),
            sa.Column("weo_subject_code", sa.TEXT, nullable=False),
            sa.Column("subject_descriptor", sa.TEXT, nullable=False),
            sa.Column("subject_notes", sa.TEXT, nullable=False),
            sa.Column("units", sa.TEXT, nullable=False),
            sa.Column("scale", sa.TEXT, nullable=False),
            sa.Column("estimates_start_after", sa.INTEGER, nullable=False),
            sa.Column("year_1980", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_1981", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_1982", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_1983", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_1984", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_1985", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_1986", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_1987", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_1988", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_1989", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_1990", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_1991", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_1992", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_1993", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_1994", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_1995", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_1996", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_1997", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_1998", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_1999", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2000", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2001", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2002", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2003", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2004", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2005", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2006", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2007", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2008", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2009", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2010", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2011", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2012", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2013", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2014", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2015", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2016", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2017", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2018", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2019", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2020", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2021", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2022", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2023", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2024", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2025", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2026", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2027", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2028", sa.DECIMAL(10, 3), nullable=True),
            sa.Column("year_2029", sa.DECIMAL(10, 3), nullable=True),
            sa.Index(None, "iso"),
            sa.Index(None, "weo_subject_code"),
            sa.Index(None, "iso", "weo_subject_code"),
            schema="public",
        )

    def get_postgres_table(self):
        return sa.Table(
            LIVE_TABLE,
            self.metadata,
            sa.Column("country_id", sa.INTEGER, nullable=True),
            sa.Column("ons_iso_alpha_3_code", sa.TEXT, nullable=True),
            sa.Column("subject_code", sa.TEXT, nullable=True),
            sa.Column("subject_descriptor", sa.TEXT, nullable=True),
            sa.Column("subject_notes", sa.TEXT, nullable=True),
            sa.Column("units", sa.TEXT, nullable=True),
            sa.Column("scale", sa.TEXT, nullable=True),
            sa.Column("year", sa.INTEGER, nullable=False),
            sa.Column("value", sa.DECIMAL(18, 3), nullable=True),
            sa.Column("estimates_start_after", sa.INTEGER, nullable=False),
            schema="public",
            keep_existing=True,
        )

    def load_data(self, delete_temp_tables=True, *args, **options):
        try:
            data = self.do_handle(prefix=settings.IMF_WORLD_ECONOMIC_OUTLOOK_S3_PREFIX)
            self.save_temp_data(data)
            self.save_import_data([])
        except Exception:
            logger.exception("import_uk_total_trade_data failed to ingest data from s3")
        finally:
            if delete_temp_tables:
                self.delete_temp_tables([TEMP_TABLE])

    def save_import_data(self, data):
        sql = f'''
            SELECT
                iso AS ons_iso_alpha_3_code,
                CASE WHEN weo_subject_code = 'NGDPD' THEN
                    'MKT_POS'
                ELSE
                    weo_subject_code
                END AS subject_code,
                subject_descriptor,
                subject_notes,
                units,
                scale,
                LTRIM(x.year, 'year_') AS year,
                CASE WHEN weo_subject_code = 'NGDPD' THEN
                    Rank() OVER (PARTITION BY year, weo_subject_code ORDER BY x.value::numeric DESC)
                ELSE
                    x.value::numeric
                END AS value,
                estimates_start_after
            FROM
                {TEMP_TABLE} AS dataset,
                jsonb_each_text(to_jsonb (dataset)) AS x (year, value)
            WHERE
                x.year LIKE 'year_%'
                AND NULLIF(TRIM(x.value), '') IS NOT NULL;
        '''

        with self.engine.connect() as connection:
            cnt = 0

            batch = connection.execute(sa.text(sql))

            for row in batch:
                try:
                    country_id = Country.objects.get(iso3=row.ons_iso_alpha_3_code).id
                except Country.DoesNotExist:
                    country_id = None

                data.append(
                    {
                        'country_id': country_id,
                        'ons_iso_alpha_3_code': row.ons_iso_alpha_3_code,
                        'subject_code': row.subject_code,
                        'subject_descriptor': row.subject_descriptor,
                        'subject_notes': row.subject_notes,
                        'units': row.units,
                        'scale': row.scale,
                        'year': row.year,
                        'value': row.value,
                        'estimates_start_after': row.estimates_start_after,
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
