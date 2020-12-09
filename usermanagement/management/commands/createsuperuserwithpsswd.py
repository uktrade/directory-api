from django.contrib.auth.management.commands import createsuperuser
from django.db import DEFAULT_DB_ALIAS


class Command(createsuperuser.Command):
    def add_arguments(self, parser):
        parser.add_argument(
            '--{}'.format(self.UserModel.USERNAME_FIELD),
            dest=self.UserModel.USERNAME_FIELD,
            default=None,
            help='Specifies the login for the superuser.',
        )
        parser.add_argument(
            '--password',
            action='store',
            default=None,
            dest='password',
            help='Specifies the password for the superuser.',
        )

        for field in self.UserModel.REQUIRED_FIELDS:
            parser.add_argument(
                '--{}'.format(field), dest=field, default=None, help='Specifies the {} for the superuser.'.format(field)
            )

    def handle(self, *args, **options):
        username = options[self.UserModel.USERNAME_FIELD]
        password = options['password']

        user_data = {}

        for field in self.UserModel.REQUIRED_FIELDS:
            user_data[field] = options[field]

        user_data[self.UserModel.USERNAME_FIELD] = username
        user_data['password'] = password

        self.UserModel._default_manager.db_manager(DEFAULT_DB_ALIAS).create_superuser(**user_data)
