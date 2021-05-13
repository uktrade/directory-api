from django.conf import settings
from django.core.files.storage import FileSystemStorage

from core import storage
from core.tests.test_views import reload_module


def test_storage_private_local():
    settings.STORAGE_CLASS_NAME = 'local-storage'
    storage_class = storage.private_storage
    assert isinstance(storage_class, FileSystemStorage)


def test_storage_private_custom_s3():
    settings.PRIVATE_FILE_STORAGE = settings.STORAGE_CLASSES['private']
    reload_module('core.storage')
    storage_class = storage.private_storage
    assert storage_class.default_acl == 'private'
