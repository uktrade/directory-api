from django.core.management import BaseCommand

from django.contrib.auth.models import User


class Command(BaseCommand):
    """Pass the username to grant staff status."""

    help = 'Used to create a supplier and company for integration tests.'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='+')

    def handle(self, *args, **options):
        for username in options['username']:
            try:
                user = User.objects.get(username=username)
                user.is_staff = True
                user.save()
                self.stdout.write(
                    self.style.SUCCESS('Successfully granted staff status user "%s"' % user.username)
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING('No user found with username "%s"' % username)
                )
