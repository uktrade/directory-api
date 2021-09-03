import urllib
from collections import defaultdict
from datetime import datetime, timedelta

from django.conf import settings

from buyer.models import Buyer
from company.models import Company, CompanyUser
from notifications import constants
from notifications.models import AnonymousEmailNotification, AnonymousUnsubscribe


def group_new_companies_by_industry():
    """
    Groups new companies (companies that published within past 7 days) by the
    industries they have selected. If a company has multiple industries then
    the company will appear multiple times.

    :returns: a dictionary
        {
            'AEROSPACE': [<Company 1>, <Company 2>],
            'AIRPORTS': [<Company 1>],
        }

    """

    days = settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS
    date_published = datetime.utcnow() - timedelta(days=days)
    companies_from_date_published = Company.objects.filter(
        date_published__gte=date_published,
    )
    companies_by_industry = defaultdict(list)
    for company in companies_from_date_published:
        for industry in company.sectors:
            companies_by_industry[industry].append(company)
    return companies_by_industry


def get_new_companies_anonymous_subscribers():
    """
    An email can subscribe to multiple industries. This removes duplicate
    email addresses and groups industries. Excludes subscribers that have
    already received "new companies in industry" email within configured
    time period.

    :returns list:
        [
            {
                'name': 'Jim Example',
                'email': 'jim@example.com',
                'industries': ['AEROSPACE', 'AIRPORTS']
            },
        ]

    """

    unsubscribers = AnonymousUnsubscribe.objects.all()
    delta = timedelta(days=settings.NEW_COMPANIES_IN_SECTOR_FREQUENCY_DAYS)
    notifications_sent_recently = AnonymousEmailNotification.objects.filter(
        category=constants.NEW_COMPANIES_IN_SECTOR, date_sent__date__gte=datetime.utcnow() - delta
    )
    exclude_emails = list(unsubscribers.values_list('email', flat=True)) + list(
        notifications_sent_recently.values_list('email', flat=True)
    )

    subscribers = {}
    for buyer in Buyer.objects.exclude(email__in=exclude_emails):
        if buyer.email not in subscribers:
            subscribers[buyer.email] = {
                'name': buyer.name,
                'email': buyer.email,
                'industries': [],
            }
        subscribers[buyer.email]['industries'].append(buyer.sector)
    return list(subscribers.values())


def get_anonymous_unsubscribe_url(uidb64, token):
    return '{base_url}?{querystring}'.format(
        base_url=settings.FAS_NOTIFICATIONS_UNSUBSCRIBE_URL,
        querystring=urllib.parse.urlencode({'uidb64': uidb64, 'token': token}),
    )


def get_unverified_suppliers(days_ago):
    letter_sent_date = datetime.utcnow() - timedelta(days=days_ago)
    return CompanyUser.objects.filter(
        company__verified_with_code=False,
        company__date_verification_letter_sent__date=letter_sent_date,
        unsubscribed=False,
    )
