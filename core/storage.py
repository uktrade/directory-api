from django.conf import settings
from django.utils.functional import LazyObject


class PrivateStorage(LazyObject):
    def _setup(self):
        self._wrapped = settings.STORAGES['private']['BACKEND']


private_storage = PrivateStorage()
