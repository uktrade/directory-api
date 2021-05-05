from django.conf import settings
from django.core.files.storage import get_storage_class
from django.utils.functional import LazyObject


class PrivateStorage(LazyObject):
    def _setup(self):
        self._wrapped = get_storage_class(settings.PRIVATE_FILE_STORAGE)()


private_storage = PrivateStorage()
