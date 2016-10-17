from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class User(AbstractBaseUser):

    # NOTE: AbstractBaseUser also implements two more fields:
    # password and last_login. Because of our architecture
    # last_login won't necessarily be reliable.
    name = models.CharField(
        _('name'),
        max_length=255,
        blank=True,
        null=True,  # serializer validation requires both null & default
        default=''
    )
    email = models.EmailField(_('email'), unique=True)
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now,
    )
    # Field from django defining access to the admin
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user '
                    'can log into this admin site.'),
    )
    terms_agreed = models.BooleanField(_('terms_agreed'), default=False)
    referrer = models.CharField(
        _('referrer'),
        max_length=255,
        blank=True,
        null=True,
        default='',  # serializer validation requires both null & default
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # email/password required by default

    def __str__(self):
        return self.email

    def get_full_name(self):
        # django method that must be implemented
        return self.name

    def get_short_name(self):
        # django method that must be implemented
        return self.name
