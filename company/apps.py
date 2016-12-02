from django.apps import AppConfig
from django.db.models.signals import post_save

from company.signals import send_verification_letter


class CompanyConfig(AppConfig):
    name = 'company'

    def ready(self):
        post_save.connect(send_verification_letter, sender='company.Company')
