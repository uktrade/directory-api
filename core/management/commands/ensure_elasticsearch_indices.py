from elasticsearch_dsl import Index

from django.core import management
from django.conf import settings


class Command(management.BaseCommand):

    help = 'Ensures the elastic search indices exists.'

    def handle(self, *args, **options):
        company_index = Index(settings.ELASTICSEARCH_COMPANY_INDEX)
        case_study_index = Index(settings.ELASTICSEARCH_CASE_STUDY_INDEX)

        if not company_index.exists() or not case_study_index.exists():
            management.call_command('rebuild_elasticsearch_index')
