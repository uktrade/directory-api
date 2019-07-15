from elasticsearch.client.indices import IndicesClient
from elasticsearch.helpers import bulk
from elasticsearch_dsl import Index, analyzer
from elasticsearch_dsl.index import connections
from elasticsearch.exceptions import NotFoundError

from django.utils.crypto import get_random_string
from django.core import management
from django.conf import settings
from django.db.models import Q

from company import documents
from company import models


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

    company_index_alias = settings.ELASTICSEARCH_COMPANY_INDEX_ALIAS
    new_company_index = None

    def __init__(self, *args, **kwargs):
        unique_id = get_random_string(length=32).lower()
        self.new_company_index = 'companies-' + unique_id
        self.client = connections.get_connection()
        super().__init__(*args, **kwargs)

    def create_index(self, name, doc_type, alias):
        index = Index(name)
        index.document(doc_type)
        index.analyzer(analyzer('english'))
        # give the index an alias (e.g, `company_alias`), so the index is used
        # when the application searches from or inserts into `campaign_alias`.
        index.aliases(**{alias: {}})  # same  as .aliases(company-alias: {})
        index.create()
        doc_type._index = index
        return index

    def get_indices(self, alias_name):
        indices_client = IndicesClient(client=self.client)
        try:
            return list(indices_client.get_alias(name=alias_name).keys())
        except NotFoundError:
            return []

    def create_new_indices(self):
        self.create_index(
            name=self.new_company_index,
            doc_type=documents.CompanyDocument,
            alias=self.company_index_alias,
        )

    def populate_new_indices(self):
        companies = (
            models.Company.objects
            .prefetch_related('supplier_case_studies')
            .filter(
                Q(is_published_find_a_supplier=True) |
                Q(is_published_investment_support_directory=True)
            )
        )
        data = []
        for company in companies:
            company_doc_type = documents.company_model_to_document(
                company=company, index=self.new_company_index,
            )
            data.append(company_doc_type.to_dict(True))
        bulk(self.client, data)

    def delete_old_indices(self):
        for index_name in self.get_indices(self.company_index_alias):
            if index_name != self.new_company_index:
                Index(index_name).delete()

    def refresh_aliases(self):
        Index(self.company_index_alias).refresh()

    def handle(self, *args, **options):
        if settings.FEATURE_FLAG_ELASTICSEARCH_REBUILD_INDEX:
            self.create_new_indices()
            self.populate_new_indices()
            self.delete_old_indices()
            self.refresh_aliases()
