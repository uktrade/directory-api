from django.conf import settings
from django.core.files.storage import get_storage_class
from django.utils.functional import LazyObject


class PrivateStorage(LazyObject):
    def _setup(self):
        self._wrapped = get_storage_class(settings.STORAGES['private']['BACKEND'])()


private_storage = PrivateStorage()
