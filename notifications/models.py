from django.db import models

from notifications import constants


class SupplierEmailNotification(models.Model):
    supplier = models.ForeignKey('supplier.Supplier')
    category = models.CharField(
        max_length=255, choices=constants.SUPPLIER_NOTIFICATION_CATEGORIES)
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{email}: {category}'.format(
            email=self.supplier.company_email,
            category=self.category,
        )


class AnonymousEmailNotification(models.Model):
    email = models.EmailField()
    category = models.CharField(
        max_length=255, choices=constants.BUYER_NOTIFICATION_CATEGORIES
    )
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{email}: {category}'.format(
            email=self.email,
            category=self.category,
        )


class AnonymousUnsubscribe(models.Model):
    """
    For allowing anonymous FAS users to unsubscribe from notifications. FAB
    suppliers are unsubscribed via `Supplier.ubsubscribed`.

    """

    email = models.EmailField(unique=True)
