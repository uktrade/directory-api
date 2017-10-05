from django.core.management.base import BaseCommand

from company import models, tasks


class Command(BaseCommand):
    help = 'Populates ElasticSearch with companies and case studies'

    def add_arguments(self, parser):
        parser.add_argument('--async', dest='async', type=bool, default=False)

    def handle(self, *args, **options):
        companies = (
            models.Company.objects
            .only('id')
            .prefetch_related('supplier_case_studies')
            .filter(is_published=True)
        )
        for company in companies:
            method = tasks.save_company_to_elasticsearch
            (method.delay if options['async'] else method)(pk=company.id)
            for casestudy in company.supplier_case_studies.all():
                method = tasks.save_case_study_to_elasticsearch
                (method.delay if options['async'] else method)(pk=casestudy.id)
