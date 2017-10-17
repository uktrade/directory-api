from django.apps import AppConfig
from django.db.models.signals import post_save

from exportopportunity import signals


class ExportReadinessConfig(AppConfig):
    name = 'exportreadiness'
