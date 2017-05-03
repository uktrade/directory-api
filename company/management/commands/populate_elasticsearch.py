from django.core.management.base import BaseCommand

from company import models, search


class Command(BaseCommand):
    help = 'Populates ElasticSearch with companies'

    def handle(self, *args, **options):
        companies = models.Company.objects.filter(is_published=True)
        for doc_type in map(search.company_model_to_doc_type, companies):
            doc_type.save()
