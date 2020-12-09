import factory
import factory.fuzzy

from company.tests.factories import CompanyUserFactory
from notifications import constants, models

SUPPLIER_CATEGORY_CHOICES = [i[0] for i in constants.SUPPLIER_NOTIFICATION_CATEGORIES]
BUYER_CATEGORY_CHOICES = [i[0] for i in constants.BUYER_NOTIFICATION_CATEGORIES]


class SupplierEmailNotificationFactory(factory.django.DjangoModelFactory):
    company_user = factory.SubFactory(CompanyUserFactory)
    category = factory.fuzzy.FuzzyChoice(SUPPLIER_CATEGORY_CHOICES)

    class Meta:
        model = models.SupplierEmailNotification


class AnonymousEmailNotificationFactory(factory.django.DjangoModelFactory):

    email = factory.Sequence(lambda n: '%d@example.com' % n)
    category = factory.fuzzy.FuzzyChoice(BUYER_CATEGORY_CHOICES)

    class Meta:
        model = models.AnonymousEmailNotification


class AnonymousUnsubscribeFactory(factory.django.DjangoModelFactory):
    email = factory.Sequence(lambda n: '%d@example.com' % n)

    class Meta:
        model = models.AnonymousUnsubscribe
