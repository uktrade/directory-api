from django.conf import settings

from notifications import constants, email, helpers


def verification_code_not_given():
    verification_code_not_given_first_reminder()
    verification_code_not_given_seconds_reminder()


def verification_code_not_given_first_reminder():
    days_ago = settings.VERIFICATION_CODE_NOT_GIVEN_DAYS
    category = constants.VERIFICATION_CODE_NOT_GIVEN
    company_users = helpers.get_unverified_suppliers(days_ago).filter(
        company__is_uk_isd_company=False,
    ).exclude(
        supplieremailnotification__category=category,
    )
    for company_user in company_users:
        notification = email.VerificationWaitingNotification(company_user)
        notification.send()


def verification_code_not_given_seconds_reminder():
    days_ago = settings.VERIFICATION_CODE_NOT_GIVEN_DAYS_2ND_EMAIL
    category = constants.VERIFICATION_CODE_2ND_EMAIL
    company_users = helpers.get_unverified_suppliers(days_ago).filter(
        company__is_uk_isd_company=False,
    ).exclude(
        supplieremailnotification__category=category,
    )
    for company_user in company_users:
        notification = email.VerificationStillWaitingNotification(company_user)
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


def company_user_unsubscribed(company_user):
    notification = email.SupplierUbsubscribed(company_user)
    notification.send()


def anonymous_unsubscribed(recipient_email):
    recipient = {'email': recipient_email, 'name': None}
    notification = email.AnonymousSubscriberUbsubscribed(recipient)
    notification.send()
