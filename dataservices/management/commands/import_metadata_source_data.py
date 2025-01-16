import json
import logging

import sqlalchemy as sa
from django.conf import settings

from dataservices import views
from dataservices.core.mixins import S3DownloadMixin
from dataservices.management.commands.helpers import BaseS3IngestionCommand, send_ingest_error_notify_email
from dataservices.models import Metadata

logger = logging.getLogger(__name__)


LIVE_TABLE = 'dataservices_metadata'
TEMP_TABLE = 'dataflow_metadata_tmp'


class Command(BaseS3IngestionCommand, S3DownloadMixin):
    help = 'Import latest release data as metadata from Data Workspace'

    def get_temp_batch(self, data, data_table):
        def get_table_data():
            for dataflow_metadata in data:
                json_data = json.loads(dataflow_metadata)

                yield (
                    (
                        data_table,
                        (
                            json_data['id'],
                            json_data['table_name'],
                            json_data['source_data_modified_utc'],
                            json_data['dataflow_swapped_tables_utc'],
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
            sa.Column("id", sa.INTEGER, nullable=False),
            sa.Column("table_name", sa.TEXT, nullable=False),
            sa.Column("source_data_modified_utc", sa.TIMESTAMP, nullable=True),
            sa.Column("dataflow_swapped_tables_utc", sa.TIMESTAMP, nullable=False),
            sa.Index(None, "id"),
            sa.Index(None, "table_name"),
            sa.Index(None, "source_data_modified_utc"),
            sa.Index(None, "dataflow_swapped_tables_utc"),
            sa.Index(None, "id", "table_name", "source_data_modified_utc", "dataflow_swapped_tables_utc"),
            schema="public",
        )

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--table',
            action='store',
            help='Specify a table to update',
            default=None,
        )

    def filter_tables(self, options, table_names_view_names):
        if options['table'] is not None:
            filtered = {}
            for t, v in table_names_view_names.items():
                if t == options['table']:
                    filtered.update({t: v})
            return filtered
        return table_names_view_names

    def load_data(self, delete_temp_tables=True, *args, **options):
        try:
            data = self.do_handle(prefix=settings.DATASETS_METADATA_S3_PREFIX)
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
                table_name,
                source_data_modified_utc as last_release
            FROM (
                SELECT
                    ROW_NUMBER() OVER (PARTITION BY table_name ORDER BY dataflow_swapped_tables_utc DESC,
                        id DESC) AS r,
                    t.*
                FROM
                    {TEMP_TABLE} t) x
            WHERE
                x.r <= 1;
        '''

        table_names_view_names = {
            'trade__uk_goods_nsa': ['TopFiveGoodsExportsByCountryView'],
            'trade__uk_services_nsa': ['TopFiveServicesExportsByCountryView'],
            'trade__uk_totals_sa': ['UKMarketTrendsView', 'UKTradeHighlightsView'],
            'world_economic_outlook__by_country': ['EconomicHighlightsView'],
        }

        with self.engine.connect() as connection:
            batch = connection.execute(sa.text(sql))

            for row in batch:
                if row.table_name in table_names_view_names.keys():
                    for view_name in table_names_view_names[row.table_name]:
                        try:
                            view = getattr(views, view_name)
                            model = view.filterset_class.Meta.model
                            instance, _created = Metadata.objects.get_or_create(view_name=view_name)
                            instance.data['source'] = {}
                            instance.data['source']['organisation'] = model.METADATA_SOURCE_ORGANISATION
                            instance.data['source']['label'] = model.METADATA_SOURCE_LABEL
                            instance.data['source']['url'] = model.METADATA_SOURCE_URL
                            instance.data['source']['last_release'] = row.last_release.isoformat()
                            instance.save()
                            self.stdout.write(
                                self.style.SUCCESS(f'Successfully updated metadata for {instance.view_name}')
                            )
                        except Exception as e:
                            self.stderr.write(self.style.ERROR(f'Error updating metadata for {view_name}'))
                            self.stderr.write(self.style.ERROR(e))
                            send_ingest_error_notify_email(view_name, e)
