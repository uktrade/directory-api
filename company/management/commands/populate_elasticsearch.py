from django.core.management.base import BaseCommand

from company import models


class Command(BaseCommand):
    help = 'Populates ElasticSearch with companies'

    def handle(self, *args, **options):
        companies = models.Company.objects.filter(is_published=True)
        for company in companies:
            company.to_doc_type().save()
