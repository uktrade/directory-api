from django.core.management.base import BaseCommand
from django.core import management

from elasticsearch_dsl import Index, analyzer

from company.search import CompanyDocType


class Command(BaseCommand):
    help = 'Rebuilds Elasticsearch companies index'

    def handle(self, *args, **options):
        companies = Index('companies')
        companies.delete(ignore=404)

        companies.doc_type(CompanyDocType)
        companies.analyzer(analyzer('english'))
        companies.create()
        management.call_command('populate_elasticsearch')
