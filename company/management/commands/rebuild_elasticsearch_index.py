from django.core.management.base import BaseCommand
from django.core import management

from elasticsearch_dsl import Index, analyzer

from django.conf import settings

from company import search


class Command(BaseCommand):
    help = 'Rebuilds Elasticsearch companies and case studies indices'

    def handle(self, *args, **options):
        indices = (
            (settings.ELASTICSEARCH_COMPANY_INDEX, search.CompanyDocType),
            (settings.ELASTICSEARCH_CASE_STUDY_INDEX, search.CaseStudyDocType),
        )
        for index_name, doc_type in indices:
            index = Index(index_name)
            index.doc_type(doc_type)
            index.analyzer(analyzer('english'))
            index.delete(ignore=404)
            index.create()

        management.call_command('populate_elasticsearch')
