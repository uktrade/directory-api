from django.conf import settings
from django.utils.functional import LazyObject


class PrivateStorage(LazyObject):
    def _setup(self):
        self._wrapped = settings.STORAGES['private']['backend']


private_storage = PrivateStorage()
