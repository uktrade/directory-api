import pandas as pd
import sqlalchemy as sa

from dataservices.models import EYBBusinessClusterInformation

from .helpers import BaseDataWorkspaceIngestionCommand


class Command(BaseDataWorkspaceIngestionCommand):
    help = 'Import ONS total UK business and employee counts per region and section, 2 and 5 digit Standard Industrial Classification'  # noqa:E501

    sql = '''
        SELECT
            nubec.geo_description,
            nubec.geo_code,
            nubec.sic_code,
            nubec.sic_description,
            nubec.total_business_count,
            nubec.business_count_release_year,
            nubec.total_employee_count,
            nubec.employee_count_release_year,
            sector_mapping.dbt_full_sector_name,
            sector_mapping.dbt_sector_name
        FROM ons.nomis__uk_business_employee_counts nubec
        LEFT JOIN (
            SELECT
                scmds."DIT full sector name" as dbt_full_sector_name,
                scmds."DIT sector" as dbt_sector_name,
                -- necessary because sic codes are stored as integer in source table meaning leading 0 was dropped
                substring(((scmds."SIC code" + 100000)::varchar) from 2 for 5) as five_digit_sic
            from public.ref_sic_codes_dit_sector_mapping scmds
        ) AS sector_mapping
        ON nubec.sic_code = sector_mapping.five_digit_sic
        WHERE nubec.geo_code <> 'K02000001'
    '''

    def load_data(self):
        data = []
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=5000)

        for chunk in chunks:
            for _idx, row in chunk.iterrows():
                data.append(
                    EYBBusinessClusterInformation(
                        geo_description=row.geo_description,
                        geo_code=row.geo_code,
                        sic_code=row.sic_code,
                        sic_description=row.sic_description,
                        total_business_count=row.total_business_count,
                        business_count_release_year=row.business_count_release_year,
                        # missing employee data represented as np.nan which results in error saving django model
                        # columns are int in dataframe so cannot store None resulting in below conditional assignment
                        total_employee_count=row.total_employee_count if row.total_employee_count > 0 else None,
                        employee_count_release_year=(
                            row.employee_count_release_year if row.employee_count_release_year > 0 else None
                        ),
                        dbt_full_sector_name=row.dbt_full_sector_name,
                        dbt_sector_name=row.dbt_sector_name,
                    )
                )

        return data
