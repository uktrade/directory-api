import pandas as pd
import sqlalchemy as sa

from dataservices.models import DBTSector

from .helpers import BaseDataWorkspaceIngestionCommand


class Command(BaseDataWorkspaceIngestionCommand):
    help = 'Import DBT sector list data from Data Workspace'
    sql = '''
        SELECT
            id,
            updated_date,
            field_01,
            field_03,
            full_sector_name,
            field_04,
            field_05,
            field_02,
            field_06,
            field_07,
            sector_cluster__april_2023
        FROM public.ref_dit_sectors
    '''

    def load_data(self):
        data = []
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=5000)

        for chunk in chunks:

            for _idx, row in chunk.iterrows():
                data.append(
                    DBTSector(
                        sector_id=row.field_01,
                        full_sector_name=row.full_sector_name,
                        sector_cluster_name=row.sector_cluster__april_2023,
                        sector_name=row.field_04,
                        sub_sector_name=row.field_05,
                        sub_sub_sector_name=row.field_02,
                    )
                )

        return data