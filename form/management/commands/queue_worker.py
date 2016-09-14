from django.core.management.base import BaseCommand

import form.queue


class Command(BaseCommand):
    help = 'Runs a queue worker'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting queue worker'))
        form.queue.Worker().run()
        self.stdout.write(self.style.SUCCESS('Queue worker finished running'))
