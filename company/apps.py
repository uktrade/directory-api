from django.apps import AppConfig
from django.db.models.signals import post_save, pre_save

from company import signals


class CompanyConfig(AppConfig):
    name = 'company'

    def ready(self):
        post_save.connect(
            receiver=signals.send_first_verification_letter,
            sender='company.Company'
        )
        post_save.connect(
            receiver=signals.save_to_elasticsearch,
            sender='company.Company'
        )
        pre_save.connect(
            receiver=signals.publish_companies_that_meet_criteria,
            sender='company.Company'
        )
        pre_save.connect(
            receiver=signals.store_date_published,
            sender='company.Company'
        )
        pre_save.connect(
            receiver=signals.deactivate_trusted_source_signup_code,
            sender='company.Company'
        )
