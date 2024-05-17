import pandas as pd
import sqlalchemy as sa

from dataservices.models import EYBSalaryData

from .helpers import BaseDataWorkspaceIngestionCommand


class Command(BaseDataWorkspaceIngestionCommand):
    help = 'Import Statista commercial rent data from Data Workspace'
    sql = '''
        SELECT
            statista.region as geo_description,
            statista.vertical,
            statista.professional_level,
            statista.median_salary,
            statista.mean_salary,
            EXTRACT(year from created) as dataworkspace_ingestion_year
        FROM statista.average_annual_salary_uk
    '''

    def load_data(self):
        data = []
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=5000)

        for chunk in chunks:
            for _idx, row in chunk.iterrows():
                data.append(
                    EYBSalaryData(
                        geo_description=row.geo_description,
                        vertical=row.vertical,
                        professional_level=row.professional_level,
                        median_salary=row.median_salary if row.median_salary > 0 else None,
                        mean_salary=row.mean_salary if row.mean_salary > 0 else None,
                        dataworkspace_ingestion_year=row.dataworkspace_ingestion_year,
                    )
                )

        return data
