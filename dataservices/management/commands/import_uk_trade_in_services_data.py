import pandas as pd
import sqlalchemy as sa
from django.conf import settings
from django.core.management import BaseCommand

from dataservices.models import Country, UKTradeInServicesByCountry


class Command(BaseCommand):
    help = 'Import ONS UK trade in services data by country from Data Workspace'

    engine = sa.create_engine(settings.DATA_WORKSPACE_DATASETS_URL, execution_options={'stream_results': True})
    sql = '''
        SELECT
            iso2,
            period,
            period_type,
            service_code,
            service_name,
            sum(imports) AS imports,
            sum(exports) AS exports
        FROM (
            SELECT
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
                ons.trade__uk_services_nsa
            WHERE
                product_code IN('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12')) s
        GROUP BY
            iso2,
            period,
            period_type,
            service_code,
            service_name;
    '''

    def handle(self, *args, **options):
        data = []
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=5000)

        for chunk in chunks:
            for _idx, row in chunk.iterrows():
                try:
                    country = Country.objects.get(iso2=row.iso2)
                except Country.DoesNotExist:
                    continue

                imports = None if row.imports != row.imports else row.imports
                exports = None if row.exports != row.exports else row.exports

                data.append(
                    UKTradeInServicesByCountry(
                        country=country,
                        period=row.period,
                        period_type=row.period_type,
                        service_code=row.service_code,
                        service_name=row.service_name,
                        imports=imports,
                        exports=exports,
                    ),
                )

        UKTradeInServicesByCountry.objects.all().delete()
        UKTradeInServicesByCountry.objects.bulk_create(data)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
