from django.apps import AppConfig
from django.db.models.signals import post_save, pre_save, post_delete

from company import signals


class CompanyConfig(AppConfig):
    name = 'company'

    def ready(self):
        pre_save.connect(
            receiver=signals.publish_companies_that_meet_criteria,
            sender='company.Company'
        )
        pre_save.connect(
            receiver=signals.store_date_published,
            sender='company.Company'
        )
        post_save.connect(
            receiver=signals.send_first_verification_letter,
            sender='company.Company'
        )
        post_save.connect(
            receiver=signals.update_company_elasticsearch_document,
            sender='company.Company'
        )
        post_save.connect(
            receiver=signals.save_case_study_change_to_elasticsearch,
            sender='company.CompanyCaseStudy',
        )
        post_delete.connect(
            receiver=signals.delete_company_elasticsearch_document,
            sender='company.Company',
        )
        post_save.connect(
            receiver=signals.send_account_ownership_transfer_notification,
            sender='company.OwnershipInvite'
        )
        post_save.connect(
            receiver=signals.send_account_collaborator_notification,
            sender='company.CollaboratorInvite'
        )
        pre_save.connect(
            receiver=signals.set_sole_trader_number,
            sender='company.Company'
        )
