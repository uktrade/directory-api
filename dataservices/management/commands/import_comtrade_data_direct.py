from django.core.management import BaseCommand
from dataservices.task_helpers import ComtradeLoader


class Command(BaseCommand):
    help = 'Comtrade data block loader'

    def handle(self, *args, **options):

        loader = ComtradeLoader()
        loader.process_all()
