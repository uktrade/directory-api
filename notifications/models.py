from django.db import models


NOTIFICATION_TYPES = (
    ('no_case_studies', 'Case studies not created'),
    ('hasnt_logged_in', 'Not logged in after first 30 days'),
    ('verification_code_not_given', 'Verification code not supplied'),
)


class SupplierNotifications(models.Model):
    supplier = models.ForeignKey('user.User')
    notification_type = models.CharField(
        max_length=255, choices=NOTIFICATION_TYPES)
    date_sent = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Supplier notifications'

    def __str__(self):
        return '{email}: {type}'.format(
            email=self.supplier.company_email,
            type=self.notification_type,
        )
