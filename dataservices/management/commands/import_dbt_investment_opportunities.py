import pandas as pd
import sqlalchemy as sa

from dataservices.models import DBTInvestmentOpportunity

from .helpers import BaseDataWorkspaceIngestionCommand


class Command(BaseDataWorkspaceIngestionCommand):
    help = 'Import DBT investment opportunities data from Data Workspace'
    sql = '''
        SELECT
            id,
            updated_date,
            investment_opportunity_code,
            opportunity_title,
            description,
            nomination_round,
            launched,
            opportunity_type,
            location,
            sub_sector,
            levelling_up,
            net_zero,
            science_technology_superpower,
            sector_cluster
        FROM public.dit_investment_opportunities
    '''

    def load_data(self):
        data = []
        chunks = pd.read_sql(sa.text(self.sql), self.engine, chunksize=5000)

        for chunk in chunks:
            for _idx, row in chunk.iterrows():
                data.append(
                    DBTInvestmentOpportunity(
                        opportunity_title=row.opportunity_title,
                        description=row.description,
                        nomination_round=row.nomination_round,
                        launched=row.launched,
                        opportunity_type=row.opportunity_type,
                        location=row.location,
                        sub_sector=row.sub_sector,
                        levelling_up=row.levelling_up,
                        net_zero=row.net_zero,
                        science_technology_superpower=row.science_technology_superpower,
                        sector_cluster=row.sector_cluster,
                    )
                )

        return data
