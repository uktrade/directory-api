import factory
import factory.fuzzy

from notifications import models
from supplier.tests.factories import SupplierFactory


CATEGORY_CHOICES = [i[0] for i in models.SUPPLIER_NOTIFICATION_CATEGORIES]


class SupplierEmailNotificationFactory(factory.django.DjangoModelFactory):

    supplier = factory.SubFactory(SupplierFactory)
    category = factory.fuzzy.FuzzyChoice(CATEGORY_CHOICES)

    class Meta:
        model = models.SupplierEmailNotification
