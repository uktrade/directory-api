from django.conf import settings
from django.utils import timezone

from company.email import CollaboratorNotification, OwnershipChangeNotification
from company.utils import send_verification_letter
from company import documents

FROM_EMAIL = settings.FAS_FROM_EMAIL


def send_first_verification_letter(sender, instance, *args, **kwargs):
    should_send_letter = all([
        settings.FEATURE_VERIFICATION_LETTERS_ENABLED,
        not instance.is_verification_letter_sent,
        not instance.verified_with_preverified_enrolment,
        instance.has_valid_address(),
    ])
    if should_send_letter:
        send_verification_letter(company=instance)


def publish_companies_that_meet_criteria(sender, instance, *args, **kwargs):
    if settings.FEATURE_MANUAL_PUBLISH_ENABLED:
        return
    if instance.is_publishable and not instance.is_published:
        instance.is_published_find_a_supplier = True


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

    notification = OwnershipChangeNotification(instance=instance)
    notification.send_async()


def send_account_collaborator_notification(
    sender, instance, created, *args, **kwargs
):
    if not created:
        return
    notification = CollaboratorNotification(instance=instance)
    notification.send_async()


def set_sole_trader_number(sender, instance, *args, **kwargs):
    if instance._state.adding and instance.company_type == sender.SOLE_TRADER:
        newest = sender.objects.all().order_by('pk').last()
        pk = newest.pk if newest else 1
        # seed operates on pk to avoid leaking primary key in the url
        number = pk + settings.SOLE_TRADER_NUMBER_SEED
        # avoids clash with companies house numbers as there is no ST prefix
        # https://www.doorda.com/kb/article/company-number-prefixes.html
        instance.number = f'ST{number:06}'
