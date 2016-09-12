from django.core.management.base import BaseCommand
from form.queue import Worker


class Command(BaseCommand):
    help = 'Runs a queue worker'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting queue worker'))
        Worker().run()
        self.stdout.write(self.style.SUCCESS('Queue worker finished running'))
