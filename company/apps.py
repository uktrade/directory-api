from django.apps import AppConfig
from django.db.models.signals import post_save, pre_save

from company import signals


class CompanyConfig(AppConfig):
    name = 'company'

    def ready(self):
        post_save.connect(
            receiver=signals.send_verification_letter,
            sender='company.Company'
        )
        pre_save.connect(
            receiver=signals.publish_companies_that_meet_criteria,
            sender='company.Company'
        )
        pre_save.connect(
            receiver=signals.fill_in_verification_date,
            sender='company.Company'
        )
