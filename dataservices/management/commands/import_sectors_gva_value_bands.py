import pandas as pd
import sqlalchemy as sa

from dataservices.models import SectorGVAValueBand

from .helpers import BaseDataWorkspaceIngestionCommand


class Command(BaseDataWorkspaceIngestionCommand):
    help = 'Import sector GVA value bands data from Data Workspace'
    sql = '''
        SELECT
            id,
            updated_date,
            sector_gva_and_value_band_id,
            full_sector_name,
            gva_grouping,
            gva_multiplier,
            value_band_a_minimum,
            value_band_b_minimum,
            value_band_c_minimum,
            value_band_d_minimum,
            value_band_e_minimum,
            sector_classification_value_band,
            sector_classification_gva_multiplier,
            start_date,
            end_date
        FROM public.ref_sectors_gva_value_bands
    '''

    def load_data(self):
        data = []
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=5000)

        for chunk in chunks:

            for _idx, row in chunk.iterrows():
                data.append(
                    SectorGVAValueBand(
                        full_sector_name=row.full_sector_name,
                        value_band_a_minimum=row.value_band_a_minimum,
                        value_band_b_minimum=row.value_band_b_minimum,
                        value_band_c_minimum=row.value_band_c_minimum,
                        value_band_d_minimum=row.value_band_d_minimum,
                        value_band_e_minimum=row.value_band_e_minimum,
                        start_date=row.start_date,
                        end_date=row.end_date,
                        sector_classification_value_band=row.sector_classification_value_band,
                        sector_classification_gva_multiplier=row.sector_classification_gva_multiplier,
                    )
                )

        return data
