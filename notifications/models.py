from django.db import models

from notifications import constants


class SupplierEmailNotification(models.Model):
    supplier = models.ForeignKey('user.User')
    category = models.CharField(
        max_length=255, choices=constants.SUPPLIER_NOTIFICATION_CATEGORIES)
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{email}: {category}'.format(
            email=self.supplier.company_email,
            category=self.category,
        )


class BuyerEmailNotification(models.Model):
    buyer = models.ForeignKey('buyer.Buyer')
    category = models.CharField(
        max_length=255, choices=constants.BUYER_NOTIFICATION_CATEGORIES)
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{email}: {category}'.format(
            email=self.buyer.email,
            category=self.category,
        )
