import pandas as pd
import sqlalchemy as sa
from django.conf import settings
from django.core.management import BaseCommand

from dataservices import views
from dataservices.management.commands.helpers import send_ingest_error_notify_email
from dataservices.models import Metadata


class Command(BaseCommand):
    help = 'Import latest release data as metadata from Data Workspace'

    engine = sa.create_engine(settings.DATA_WORKSPACE_DATASETS_URL, execution_options={'stream_results': True})
    sql = '''
        SELECT
            table_name,
            source_data_modified_utc as last_release
        FROM (
            SELECT
                ROW_NUMBER() OVER (PARTITION BY table_name ORDER BY dataflow_swapped_tables_utc DESC,
                    id DESC) AS r,
                t.*
            FROM
                dataflow.metadata t) x
        WHERE
            x.r <= 1;
    '''

    def add_arguments(self, parser):
        parser.add_argument(
            '--table',
            action='store',
            help='Specify a table to update',
            default=None,
        )

    def handle(self, *args, **options):
        table_names_view_names = {
            'trade__uk_goods_nsa': ['TopFiveGoodsExportsByCountryView'],
            'trade__uk_services_nsa': ['TopFiveServicesExportsByCountryView'],
            'trade__uk_totals_sa': ['UKMarketTrendsView', 'UKTradeHighlightsView'],
            'world_economic_outlook__by_country': ['EconomicHighlightsView'],
        }
        records = pd.read_sql(sa.text(self.sql), self.engine)

        table_names_view_names = self.filter_tables(options, table_names_view_names)

        for _idx, row in records.iterrows():
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
                        self.stdout.write(self.style.SUCCESS(f'Successfully updated metadata for {instance.view_name}'))
                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f'Error updating metadata for {view_name}'))
                        self.stderr.write(self.style.ERROR(e))
                        send_ingest_error_notify_email(view_name, e)

    def filter_tables(self, options, table_names_view_names):
        if options['table'] is not None:
            filtered = {}
            for t, v in table_names_view_names.items():
                if t == options['table']:
                    filtered.update({t: v})
            return filtered
        return table_names_view_names
