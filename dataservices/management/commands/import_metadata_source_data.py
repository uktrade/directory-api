import pandas as pd
import sqlalchemy as sa
from django.conf import settings
from django.core.management import BaseCommand

from dataservices import views
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

    def handle(self, *args, **options):
        table_names_view_names = {
            'trade__uk_goods_nsa': ['TopFiveGoodsExportsByCountryView'],
            'trade__uk_services_nsa': ['TopFiveServicesExportsByCountryView'],
            'trade__uk_totals_sa': ['UKMarketTrendsView', 'UKTradeHighlightsView'],
            'world_economic_outlook__by_country': ['EconomicHighlightsView'],
        }
        records = pd.read_sql(sa.text(self.sql), self.engine)

        for _idx, row in records.iterrows():
            if row.table_name in table_names_view_names.keys():
                for view_name in table_names_view_names[row.table_name]:
                    view = getattr(views, view_name)
                    model = view.filter_class.Meta.model
                    instance, _created = Metadata.objects.get_or_create(view_name=view_name)
                    instance.data['source'] = {}
                    instance.data['source']['organisation'] = model.METADATA_SOURCE_ORGANISATION
                    instance.data['source']['label'] = model.METADATA_SOURCE_LABEL
                    instance.data['source']['url'] = model.METADATA_SOURCE_URL
                    instance.data['source']['last_release'] = row.last_release.isoformat()
                    instance.save()

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
