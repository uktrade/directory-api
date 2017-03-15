import urllib
from collections import defaultdict
from datetime import datetime, timedelta

from django.core.signing import Signer
from django.conf import settings

from buyer.models import Buyer
from company.models import Company
from notifications.models import AnonymousUnsubscribe


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


def get_anonymous_subscribers():
    """
    An email can subscribe to multiple industries. This removes duplicate
    email addresses and groups industries.

    :returns list:
        [
            {
                'name': 'Jim Example',
                'email': 'jim@example.com',
                'industries': ['AEROSPACE', 'AIRPORTS']
            },
        ]

    """

    exclude_emails = (
        AnonymousUnsubscribe.objects.all().values_list('email', flat=True)
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


def get_anonymous_unsubscribe_url(email):
    return '{base_url}?{querystring}'.format(
        base_url=settings.FAB_NOTIFICATIONS_UNSUBSCRIBE_URL,
        querystring=urllib.parse.urlencode({'email': Signer().sign(email)}),
    )
