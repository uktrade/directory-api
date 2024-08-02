import pandas as pd
import sqlalchemy as sa

from dataservices.models import EYBSalaryData

from .helpers import BaseDataWorkspaceIngestionCommand, align_vertical_names


class Command(BaseDataWorkspaceIngestionCommand):
    help = 'Import Statista salary data from Data Workspace'
    sql = '''
        SELECT
            statista.region as geo_description,
            statista.vertical,
            statista.professional_level,
            statista.occupation,
            statista.code,
            statista.median_salary,
            statista.mean_salary,
            statista.year
        FROM statista.average_annual_salary_uk statista
    '''

    def load_data(self):
        data = []
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=5000)

        for chunk in chunks:
            # in the source data some of the salary columns contain 'x', ':' and so on. Also represented as strings
            chunk = chunk.replace(
                to_replace={'mean_salary': r'[^0-9.]', 'median_salary': r'[^0-9.]'}, value='0', regex=True
            )
            chunk = chunk.fillna(value='0')
            chunk = chunk.astype({'mean_salary': 'int32', 'median_salary': 'int32'})

            for _idx, row in chunk.iterrows():
                data.append(
                    EYBSalaryData(
                        geo_description=row.geo_description.strip(),
                        vertical=align_vertical_names(row.vertical.strip()),
                        professional_level=row.professional_level.strip(),
                        occupation=row.occupation.strip(),
                        soc_code=row.code,
                        median_salary=row.median_salary,
                        mean_salary=row.mean_salary,
                        dataset_year=row.year,
                    )
                )

        return data
