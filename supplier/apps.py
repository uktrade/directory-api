from django.apps import AppConfig

from django.db.models.signals import post_save

from supplier.signals import send_confirmation_email


class SupplierConfig(AppConfig):
    name = 'supplier'

    def ready(self):
        post_save.connect(send_confirmation_email, sender='user.User')
