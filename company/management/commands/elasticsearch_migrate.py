from django.conf import settings
from django.core import management
from django.db.models import Q
from django.utils.crypto import get_random_string
from opensearchpy.helpers import bulk
from opensearch_dsl.connections import connections

from company import documents, models

ALIAS = settings.OPENSEARCH_COMPANY_INDEX_ALIAS
PREFIX = 'companies-'
PATTERN = f'{PREFIX}*'


class Command(management.BaseCommand):
    help = """
    Migrate Elasticsearch indices with zero downtime - meaning that search will
    still work during the migration. The migration has four steps:

    1) Create the new indices: create company index and give
       them the appropriate alias so the new indices will be used when the
       application searches from or inserts into the company.
    2) Populate the new indices: insert the companies into the
       new indices. This is done in bulk for performance gains.
    3) Delete the old indices: If a search happens during the migration the
       old indices will be used but now the new indices are ready so the old
       indices can be deleted - and the application will now search from and
       insert into the new indices.
    4) Refresh the new aliases: Block execution until the new indices have all
       their operations complete. This is critical to avoid race conditions.

    """

    new_index_name = None

    def __init__(self, *args, **kwargs):
        unique_id = get_random_string(length=32).lower()
        self.new_index_name = f'{PREFIX}{unique_id}'
        self.client = connections.get_connection()
        super().__init__(*args, **kwargs)

    def create_index_template(self):
        index_template = documents.CompanyDocument._index.as_template(ALIAS, PATTERN)
        index_template.save()

    def populate_new_indices(self):
        companies = models.Company.objects.prefetch_related('supplier_case_studies').filter(
            Q(is_published_find_a_supplier=True) | Q(is_published_investment_support_directory=True)
        )
        data = []
        for company in companies:
            company_doc_type = documents.company_model_to_document(company=company, index=self.new_index_name)
            data.append(company_doc_type.to_dict(True))
        bulk(self.client, data)

    def update_aliases(self):
        actions = [
            {'remove': {'alias': ALIAS, 'index': PATTERN}},
            {'add': {'alias': ALIAS, 'index': self.new_index_name}},
        ]
        self.client.indices.update_aliases(body={'actions': actions})

    def handle(self, *args, **options):
        if settings.FEATURE_FLAG_OPENSEARCH_REBUILD_INDEX:
            self.create_index_template()
            self.client.indices.create(self.new_index_name)
            self.populate_new_indices()
            self.update_aliases()
