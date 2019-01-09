from datetime import timedelta, datetime

from django.conf import settings

from directory_sso_api_client.client import sso_api_client

from notifications import constants, email, helpers
from supplier.models import Supplier


def no_case_studies():
    now = datetime.utcnow()
    days_ago = now - timedelta(days=settings.NO_CASE_STUDIES_DAYS)
    suppliers = Supplier.objects.filter(
        company__supplier_case_studies__isnull=True,
        date_joined__year=days_ago.year,
        date_joined__month=days_ago.month,
        date_joined__day=days_ago.day,
        unsubscribed=False,
    ).exclude(
        supplieremailnotification__category=constants.NO_CASE_STUDIES,
    )
    for supplier in suppliers:
        notification = email.NoCaseStudiesNotification(supplier)
        notification.send()


def hasnt_logged_in():
    now = datetime.utcnow()
    days_ago = now - timedelta(days=settings.HASNT_LOGGED_IN_DAYS)
    start_datetime = days_ago.replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end_datetime = days_ago.replace(
        hour=23, minute=59, second=59, microsecond=999999
    )

    login_data = sso_api_client.user.get_last_login(
        start=start_datetime, end=end_datetime
    ).json()

    sso_ids = [sso_user['id'] for sso_user in login_data]
    suppliers = Supplier.objects.filter(
        sso_id__in=sso_ids
    ).exclude(
        supplieremailnotification__category=constants.HASNT_LOGGED_IN,
    )

    for supplier in suppliers:
        notification = email.HasNotLoggedInRecentlyNotification(supplier)
        notification.send()


def verification_code_not_given():
    verification_code_not_given_first_reminder()
    verification_code_not_given_seconds_reminder()


def verification_code_not_given_first_reminder():
    days_ago = settings.VERIFICATION_CODE_NOT_GIVEN_DAYS
    category = constants.VERIFICATION_CODE_NOT_GIVEN
    suppliers = helpers.get_unverified_suppliers(days_ago).exclude(
        supplieremailnotification__category=category,
    )
    for supplier in suppliers:
        notification = email.VerificationWaitingNotification(supplier)
        notification.send()


def verification_code_not_given_seconds_reminder():
    days_ago = settings.VERIFICATION_CODE_NOT_GIVEN_DAYS_2ND_EMAIL
    category = constants.VERIFICATION_CODE_2ND_EMAIL
    suppliers = helpers.get_unverified_suppliers(days_ago).exclude(
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
