import multiprocessing

from django.conf import settings
from django.core.management.base import BaseCommand

import form.queue


class Command(BaseCommand):
    help = 'Runs a queue worker'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting queue worker'))

        worker = form.queue.Worker()

        for x in range(settings.SQS_QUEUE_WORKER_PROCESSES_NUMBER):
            worker_process = multiprocessing.Process(target=worker.run)
            worker_process.daemon = True
            worker_process.start()

        self.stdout.write(self.style.SUCCESS('Queue worker finished running'))
