from datetime import timedelta, datetime

from django.conf import settings

from directory_sso_api_client.client import sso_api_client

from notifications import constants, email, helpers
from supplier.models import Supplier


def verification_code_not_given():
    verification_code_not_given_first_reminder()
    verification_code_not_given_seconds_reminder()


def verification_code_not_given_first_reminder():
    days_ago = settings.VERIFICATION_CODE_NOT_GIVEN_DAYS
    category = constants.VERIFICATION_CODE_NOT_GIVEN
    suppliers = helpers.get_unverified_suppliers(days_ago).filter(
        company__is_uk_isd_company=False,
    ).exclude(
        supplieremailnotification__category=category,
    )
    for supplier in suppliers:
        notification = email.VerificationWaitingNotification(supplier)
        notification.send()


def verification_code_not_given_seconds_reminder():
    days_ago = settings.VERIFICATION_CODE_NOT_GIVEN_DAYS_2ND_EMAIL
    category = constants.VERIFICATION_CODE_2ND_EMAIL
    suppliers = helpers.get_unverified_suppliers(days_ago).filter(
        company__is_uk_isd_company=False,
    ).exclude(
        supplieremailnotification__category=category,
    )
    for supplier in suppliers:
        notification = email.VerificationStillWaitingNotification(supplier)
        notification.send()


def new_companies_in_sector():
    companies_grouped_by_industry = helpers.group_new_companies_by_industry()

    for subscriber in helpers.get_new_companies_anonymous_subscribers():
        companies = set()
        for industry in subscriber['industries']:
            companies.update(companies_grouped_by_industry[industry])
        if companies:
            notification = email.NewCompaniesInSectorNotification(
                subscriber=subscriber, companies=companies
            )
            notification.send()


def supplier_unsubscribed(supplier):
    notification = email.SupplierUbsubscribed(supplier)
    notification.send()


def anonymous_unsubscribed(recipient_email):
    recipient = {'email': recipient_email, 'name': None}
    notification = email.AnonymousSubscriberUbsubscribed(recipient)
    notification.send()
