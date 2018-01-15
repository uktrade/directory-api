from django.apps import AppConfig
from django.db.models.signals import post_save

from supplier import signals


class SupplierConfig(AppConfig):
    name = 'supplier'

    def ready(self):
        post_save.connect(
            receiver=signals.remove_supplier_company_ownership,
            sender='supplier.Supplier'
        )
