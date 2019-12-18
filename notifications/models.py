from django.db import models

from notifications import constants


class SupplierEmailNotification(models.Model):
    company_user = models.ForeignKey('company.CompanyUser', null=True, blank=True, on_delete=models.SET)
    category = models.CharField(max_length=255, choices=constants.SUPPLIER_NOTIFICATION_CATEGORIES)
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.company_user.company_email}: {self.category}'


class AnonymousEmailNotification(models.Model):
    email = models.EmailField()
    category = models.CharField(max_length=255, choices=constants.BUYER_NOTIFICATION_CATEGORIES)
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.email}: {self.category}'


class AnonymousUnsubscribe(models.Model):
    """
    For allowing anonymous FAS users to unsubscribe from notifications. FAB
    suppliers are unsubscribed via `Supplier.ubsubscribed`.

    """

    email = models.EmailField(unique=True)
