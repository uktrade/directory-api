from django.conf import settings
from django.core.files.storage import get_storage_class
from django.utils.functional import LazyObject
from pydoc import locate


class PrivateStorage(LazyObject):
    def _setup(self):
        my_class = locate(settings.STORAGES['private']['BACKEND'])
        self._wrapped = my_class()

private_storage = PrivateStorage()
