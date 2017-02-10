from django.db import models


SUPPLIER_NOTIFICATION_CATEGORIES = (
    ('no_case_studies', 'Case studies not created'),
    ('hasnt_logged_in', 'Not logged in after first 30 days'),
    ('verification_code_not_given', 'Verification code not supplied'),
)


class SupplierEmailNotification(models.Model):
    supplier = models.ForeignKey('user.User')
    category = models.CharField(
        max_length=255, choices=SUPPLIER_NOTIFICATION_CATEGORIES)
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{email}: {category}'.format(
            email=self.supplier.company_email,
            category=self.category,
        )
