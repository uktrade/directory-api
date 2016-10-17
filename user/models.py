from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class User(AbstractBaseUser):

    name = models.CharField(_('name'), max_length=255)
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
    # Field from django that is used to validate user in oauth library
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    terms_agreed = models.BooleanField()
    referrer = models.CharField(max_length=255)

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
