import factory
import factory.fuzzy

from notifications import models
from supplier.tests.factories import SupplierFactory
from buyer.tests.factories import BuyerFactory


SUPPLIER_CATEGORY_CHOICES = [
    i[0] for i in models.SUPPLIER_NOTIFICATION_CATEGORIES]
BUYER_CATEGORY_CHOICES = [
    i[0] for i in models.BUYER_NOTIFICATION_CATEGORIES]


class SupplierEmailNotificationFactory(factory.django.DjangoModelFactory):

    supplier = factory.SubFactory(SupplierFactory)
    category = factory.fuzzy.FuzzyChoice(SUPPLIER_CATEGORY_CHOICES)

    class Meta:
        model = models.SupplierEmailNotification


class BuyerEmailNotificationFactory(factory.django.DjangoModelFactory):

    buyer = factory.SubFactory(BuyerFactory)
    category = factory.fuzzy.FuzzyChoice(BUYER_CATEGORY_CHOICES)

    class Meta:
        model = models.BuyerEmailNotification
