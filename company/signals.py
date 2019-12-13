from django.conf import settings
from django.utils import timezone
import datetime

from directory_constants import company_types, user_roles
from company import email, documents, helpers, models

FROM_EMAIL = settings.FAS_FROM_EMAIL


def send_first_verification_letter(sender, instance, *args, **kwargs):
    should_send_letter = all([
        settings.FEATURE_VERIFICATION_LETTERS_ENABLED,
        not instance.is_verification_letter_sent,
        not instance.verified_with_preverified_enrolment,
        instance.company_type == company_types.COMPANIES_HOUSE,
        instance.has_valid_address(),
    ])
    if should_send_letter:
        helpers.send_verification_letter(
            company=instance,
            form_url='send_first_verification_letter',
        )


def send_company_registration_letter(sender, instance, *args, **kwargs):
    FEATURE_IMPLEMENTATION_DATE = datetime.datetime(2019, 10, 15, tzinfo=timezone.utc)

    should_send_letter = all([
        settings.FEATURE_REGISTRATION_LETTERS_ENABLED,
        not instance.is_registration_letter_sent,
        instance.company_type == company_types.COMPANIES_HOUSE,
        bool(instance.address_line_1 and instance.postal_code),
        instance.company_users.exists(),
        instance.created > FEATURE_IMPLEMENTATION_DATE,
    ])

    if should_send_letter:
        helpers.send_registration_letter(
            company=instance,
            form_url='send_company_claimed_letter_automatically_sent',
        )


def store_date_published(sender, instance, *args, **kwargs):
    if instance.is_published and not instance.date_published:
        instance.date_published = timezone.now()


def update_company_elasticsearch_document(sender, instance, *args, **kwargs):
    document = documents.company_model_to_document(instance)
    if instance.is_published:
        document.save()
    else:
        document.delete(ignore=404)


def delete_company_elasticsearch_document(sender, instance, *args, **kwargs):
    document = documents.company_model_to_document(instance)
    document.delete(ignore=404)


def save_case_study_change_to_elasticsearch(sender, instance, *args, **kwargs):
    if instance.company.is_published:
        document = documents.company_model_to_document(instance.company)
        document.save()


def send_account_ownership_transfer_notification(
    sender, instance, created, *args, **kwargs
):
    if not created:
        return

    notification = email.OwnershipChangeNotification(instance=instance)
    notification.send_async()


def send_new_invite_collaboration_notification(sender, instance, created, *args, **kwargs):
    if not created:
        return

    existing_company = helpers.get_user_company(collaboration_invite=instance, companies=models.Company.objects.all())
    if existing_company:
        helpers.send_new_user_invite_email_existing_company(
            collaboration_invite=instance,
            existing_company_name=existing_company.name,
            form_url='send_new_invite_collaborator_notification_existing',
        )
    else:
        helpers.send_new_user_invite_email(
            collaboration_invite=instance,
            form_url='send_new_invite_collaborator_notification'
        )


def send_account_collaborator_notification(sender, instance, created, *args, **kwargs):
    if not created:
        return
    notification = email.CollaboratorNotification(instance=instance)
    notification.send_async()


def set_non_companies_house_number(sender, instance, *args, **kwargs):
    if (
        instance._state.adding
        and instance.company_type != company_types.COMPANIES_HOUSE
    ):
        newest = sender.objects.all().order_by('pk').last()
        pk = newest.pk if newest else 1
        # seed operates on pk to avoid leaking primary key in the url
        number = pk + settings.SOLE_TRADER_NUMBER_SEED
        company_prefix = helpers.company_prefix_map[instance.company_type]
        # avoids clash with companies house numbers as there is no ST prefix
        # https://www.doorda.com/kb/article/company-number-prefixes.html
        instance.number = f'{company_prefix}{number:06}'


def send_acknowledgement_admin_email_on_invite_accept(sender, instance, *args, **kwargs):
    if not instance._state.adding:
        pre_save_instance = sender.objects.get(pk=instance.pk)
        if instance.accepted and not pre_save_instance.accepted:
            company_user_name = helpers.get_company_user_alias_by_email(
                collaboration_invite=instance,
                company_users=models.CompanyUser.objects.all()
            )
            helpers.send_new_user_alert_invite_accepted_email(
                collaboration_invite=instance,
                collaborator_name=company_user_name,
                form_url='send_acknowledgement_admin_email_on_invite_accept'
            )


def send_admins_new_collaboration_request_notification(sender, instance, *args, **kwargs):
    if instance._state.adding:
        admins = instance.requestor.company.company_users.filter(role=user_roles.ADMIN)
        helpers.send_admins_new_collaboration_request_email(
                company_admins=admins,
                collaboration_request=instance,
                form_url='send_admins_new_collaboration_request_email'
        )


def send_user_collaboration_request_email_on_decline(sender, instance, *args, **kwargs):
    if not instance.accepted:
        helpers.send_user_collaboration_request_declined_email(
                collaboration_request=instance,
                form_url='send_user_collaboration_request_email_on_decline'
        )


def send_user_collaboration_request_email_on_accept(sender, instance, *args, **kwargs):
    if not instance._state.adding:
        pre_save_instance = sender.objects.get(pk=instance.pk)
        if instance.accepted and not pre_save_instance.accepted:
            helpers.send_user_collaboration_request_accepted_email(
                    collaboration_request=instance,
                    form_url='send_user_collaboration_request_email_on_accept'
            )
