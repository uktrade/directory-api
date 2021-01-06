from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save, pre_save


class CompanyConfig(AppConfig):
    name = 'company'

    def ready(self):
        from company import signals

        pre_save.connect(receiver=signals.store_date_published, sender='company.Company')
        post_save.connect(receiver=signals.send_first_verification_letter, sender='company.Company')
        post_save.connect(receiver=signals.send_company_registration_letter, sender='company.Company')
        post_save.connect(receiver=signals.update_company_elasticsearch_document, sender='company.Company')
        post_save.connect(
            receiver=signals.save_case_study_change_to_elasticsearch,
            sender='company.CompanyCaseStudy',
        )
        post_delete.connect(
            receiver=signals.delete_company_elasticsearch_document,
            sender='company.Company',
        )
        pre_save.connect(receiver=signals.set_non_companies_house_number, sender='company.Company')
        post_save.connect(
            receiver=signals.send_new_invite_collaboration_notification, sender='company.CollaborationInvite'
        )
        pre_save.connect(
            receiver=signals.send_acknowledgement_admin_email_on_invite_accept, sender='company.CollaborationInvite'
        )
        pre_save.connect(
            receiver=signals.send_admins_new_collaboration_request_notification, sender='company.CollaborationRequest'
        )
        pre_save.connect(
            receiver=signals.send_user_collaboration_request_email_on_accept, sender='company.CollaborationRequest'
        )
        post_delete.connect(
            receiver=signals.send_user_collaboration_request_email_on_decline, sender='company.CollaborationRequest'
        )
