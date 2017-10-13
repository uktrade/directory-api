from elasticsearch.client.indices import IndicesClient
from elasticsearch.helpers import bulk
from elasticsearch_dsl import Index, analyzer
from elasticsearch_dsl.index import connections
from elasticsearch.exceptions import NotFoundError

from django.utils.crypto import get_random_string
from django.core import management
from django.conf import settings

from company import search
from company import models


class Command(management.BaseCommand):

    help = 'Migrate elasticsearch indices.'

    company_index_alias = settings.ELASTICSEARCH_COMPANY_INDEX_ALIAS
    case_study_index_alias = settings.ELASTICSEARCH_CASE_STUDY_INDEX_ALIAS
    case_study_index_prefix = settings.ELASTICSEARCH_CASE_STUDY_INDEX
    company_index_prefix = settings.ELASTICSEARCH_COMPANY_INDEX
    new_company_index = None
    new_case_study_index = None

    def __init__(self, *args, **kwargs):
        unique_id = get_random_string(length=32).lower()
        self.new_company_index = self.company_index_prefix + unique_id
        self.new_case_study_index = self.case_study_index_prefix + unique_id
        self.client = connections.get_connection()
        super().__init__(*args, **kwargs)

    def create_index(self, name, doc_type, alias):
        index = Index(name)
        index.doc_type(doc_type)
        index.analyzer(analyzer('english'))
        index.aliases(**{alias: {}})
        index.create()
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
            doc_type=search.CompanyDocType,
            alias=self.company_index_alias,
        )
        self.create_index(
            name=self.new_case_study_index,
            doc_type=search.CaseStudyDocType,
            alias=self.case_study_index_alias,
        )

    def populate_new_indices(self):
        companies = (
            models.Company.objects
            .prefetch_related('supplier_case_studies')
            .filter(is_published=True)
        )
        company_documents = []
        case_study_documents = []
        for company in companies:
            company_doc_type = search.company_model_to_doc_type(
                company=company, index=self.new_company_index,
            )
            company_documents.append(company_doc_type.to_dict(True))
            for case_study in company.supplier_case_studies.all():
                case_study_doc_type = search.case_study_model_to_doc_type(
                    case_study=case_study, index=self.new_case_study_index,
                )
                case_study_documents.append(case_study_doc_type.to_dict(True))
        bulk(self.client, company_documents)
        bulk(self.client, case_study_documents)

    def delete_old_indices(self):
        for index_name in self.get_indices(self.company_index_alias):
            if index_name != self.new_company_index:
                Index(index_name).delete()
        for index_name in self.get_indices(self.case_study_index_alias):
            if index_name != self.new_case_study_index:
                Index(index_name).delete()

    def refresh_aliases(self):
        Index(self.company_index_alias).refresh()
        Index(self.case_study_index_alias).refresh()

    def handle(self, *args, **options):
        self.create_new_indices()
        self.populate_new_indices()
        self.delete_old_indices()
        self.refresh_aliases()
