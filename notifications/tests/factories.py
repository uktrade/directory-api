import factory
import factory.fuzzy

from notifications import models
from supplier.tests.factories import SupplierFactory


class SupplierNotificationsFactory(factory.django.DjangoModelFactory):

    supplier = factory.SubFactory(SupplierFactory)
    notification_type = factory.fuzzy.FuzzyChoice(models.NOTIFICATION_TYPES)

    class Meta:
        model = models.SupplierNotifications
