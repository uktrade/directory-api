import pandas as pd
import sqlalchemy as sa

from dataservices.models import Country, WorldEconomicOutlookByCountry

from .helpers import MarketGuidesDataIngestionCommand


class Command(MarketGuidesDataIngestionCommand):
    help = 'Import IMF world economic outlook data by country from Data Workspace'

    sql = '''
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
            imf.world_economic_outlook__by_country AS dataset,
            jsonb_each_text(to_jsonb (dataset)) AS x (year, value)
        WHERE
            weo_subject_code IN('NGDPD', 'NGDPDPC', 'NGDP_RPCH')
            AND x.year LIKE 'year_%'
            AND NULLIF(TRIM(x.value), '') IS NOT NULL;
    '''

    def add_arguments(self, parser):
        parser.add_argument(
            '--write',
            action='store_true',
            help='Store dataset records',
        )

    def load_data(self):
        data = []
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=10000)

        for chunk in chunks:
            for _idx, row in chunk.iterrows():
                try:
                    country = Country.objects.get(iso3=row.ons_iso_alpha_3_code)
                except Country.DoesNotExist:
                    country = None

                data.append(
                    WorldEconomicOutlookByCountry(
                        country=country,
                        ons_iso_alpha_3_code=row.ons_iso_alpha_3_code,
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

        return data
