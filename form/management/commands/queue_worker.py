import logging

from django.core.management.base import BaseCommand

import form.queue


class Command(BaseCommand):
    help = 'Runs a form data SQS queue worker'

    @staticmethod
    def setup_logging():
        logger = logging.getLogger()
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(console)

    def handle(self, *args, **options):
        self.setup_logging()

        self.stdout.write(
            self.style.SUCCESS('Starting queue worker')
        )

        form.queue.Worker().run()

        self.stdout.write(
            self.style.SUCCESS('Queue worker finished running')
        )
