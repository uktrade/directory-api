import pandas as pd
import sqlalchemy as sa

from dataservices.models import EYBCommercialPropertyRent

from .helpers import BaseDataWorkspaceIngestionCommand


class Command(BaseDataWorkspaceIngestionCommand):
    help = 'Import Statista commercial rent data from Data Workspace'
    sql = '''
        SELECT
            statista.region as geo_description,
            statista.vertical,
            statista.sub_vertical,
            statista.gbp_per_square_foot_per_month,
            statista.square_feet,
            statista.gbp_per_month,
            statista.release_year
        FROM statista.commercial_property_rent statista
    '''

    def load_data(self):
        data = []
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=5000)

        for chunk in chunks:
            for _idx, row in chunk.iterrows():
                data.append(
                    EYBCommercialPropertyRent(
                        geo_description=row.geo_description,
                        vertical=row.vertical,
                        sub_vertical=row.sub_vertical,
                        gbp_per_square_foot_per_month=(
                            row.gbp_per_square_foot_per_month if row.gbp_per_month > 0 else None
                        ),
                        square_feet=row.square_feet if row.square_feet > 0 else None,
                        gbp_per_month=row.gbp_per_month if row.gbp_per_month > 0 else None,
                        dataset_year=row.release_year,
                    )
                )

        return data
