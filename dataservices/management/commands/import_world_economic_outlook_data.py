import pandas as pd
import sqlalchemy as sa
from django.conf import settings
from django.core.management import BaseCommand

from dataservices.models import Country, WorldEconomicOutlookByCountry


class Command(BaseCommand):
    help = 'Import IMF world economic outlook data by country from Data Workspace'

    imf_economic_growth_descriptor = 'NGDP_RPCH'
    imf_gdp_per_capita_descriptor = 'NGDPDPC'

    engine = sa.create_engine(settings.DATA_WORKSPACE_DATASETS_URL, execution_options={'stream_results': True})
    sql = '''
        SELECT
            iso AS iso3,
            weo_subject_code AS subject_code,
            subject_descriptor,
            subject_notes,
            units,
            scale,
            LTRIM(x.year, 'year_') AS year,
            x.value,
            estimates_start_after
        FROM
            imf.world_economic_outlook__by_country AS dataset,
            jsonb_each_text(to_jsonb (dataset)) AS x (year,
                value)
        WHERE
            weo_subject_code IN('NGDPDPC', 'NGDP_RPCH')
            AND x.year LIKE 'year_%'
            AND NULLIF(TRIM(x.value), '') IS NOT NULL;
    '''

    def handle(self, *args, **options):
        data = []
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=10000)

        for chunk in chunks:
            for _idx, row in chunk.iterrows():
                try:
                    country = Country.objects.get(iso3=row.iso3)
                except Country.DoesNotExist:
                    continue

                data.append(
                    WorldEconomicOutlookByCountry(
                        country=country,
                        subject_code=row.subject_code,
                        subject_descriptor=row.subject_descriptor,
                        subject_notes=row.subject_notes,
                        units=row.units,
                        scale=row.scale,
                        year=row.year,
                        value=row.value,
                        estimates_start_after=row.estimates_start_after,
                    )
                )

        WorldEconomicOutlookByCountry.objects.all().delete()
        WorldEconomicOutlookByCountry.objects.bulk_create(data)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
