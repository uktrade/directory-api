from django.conf import settings
from django.core.signing import Signer
from django.db import models
from directory_validators import enrolment as shared_validators

from api.model_utils import TimeStampedModel


class TrustedSourceSignupCode(TimeStampedModel):
    company_number = models.CharField(
        max_length=8,
        validators=[shared_validators.company_number],
        # can be in multiple trade organisations, so don't enforce uniqueness
    )
    email_address = models.EmailField()
    code = models.CharField(
        max_length=1000,
        unique=True
    )
    generated_for = models.CharField(
        max_length=1000,
        help_text='The trade organisation the code was created for.'
    )
    generated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        help_text='The admin account that created the code.',
        null=True,
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.pk:
            self.code = Signer().sign(self.email_address)
        return super().save(*args, **kwargs)

    @property
    def enrolment_link(self):
        link_template = settings.FAB_TRUSTED_SOURCE_ENROLMENT_LINK
        return link_template.format(code=self.code)
