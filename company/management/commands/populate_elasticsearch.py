from django.core.management.base import BaseCommand

from company import models, tasks


class Command(BaseCommand):
    help = 'Populates ElasticSearch with companies'

    def handle(self, *args, **options):
        for company_id in models.Company.objects.filter(
                is_published=True
        ).values_list(
            'id', flat=True
        ):
            tasks.save_company_to_elasticsearch(company_id=company_id)
