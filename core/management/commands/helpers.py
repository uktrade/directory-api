import time

from django.conf import settings


class ExclusiveDistributedHandleMixin:

    help = (
        'Only one instance will run the migrations. All others will wait for '
        'the migrations to be completed...or fail resulting in deployment '
        'timing out.'
    )

    def handle(self, *args, **options):
        if self.is_first_instance():
            return super().handle(*args, **options)
        else:
            while self.is_migration_pending():
                time.sleep(1)

    @staticmethod
    def is_first_instance():
        # VCAP_APPLICATION will be empty on non-paas environments, so assume
        # the current instance is the only instance on non-paas
        return settings.VCAP_APPLICATION.get('instance_index', 0) == 0

    def is_migration_pending(self):
        raise NotImplementedError
