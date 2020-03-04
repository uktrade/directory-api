from directory_validators.string import no_html

from django.db import models

from core.helpers import TimeStampedModel


class PreVerifiedEnrolment(TimeStampedModel):
    company_number = models.CharField(max_length=8, validators=[no_html])
    company_name = models.TextField(validators=[no_html], null=True, blank=True)
    email_address = models.EmailField(blank=True, null=True)
    generated_for = models.CharField(max_length=1000, help_text='The trade organisation the code was created for.')
    generated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        help_text='The admin account that created the code.',
        null=True,
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.company_number

    class Meta:
        unique_together = ['company_number', 'email_address']
