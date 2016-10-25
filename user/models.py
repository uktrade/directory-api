from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from company.models import Company


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, company_email, password, **extra_fields):
        if not company_email:
            raise ValueError('The given company_email must be set')
        # TODO: use SSO, username / pass will change
        company_email = self.normalize_email(company_email)
        user = self.model(company_email=company_email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, company_email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(company_email, password, **extra_fields)

    def create_superuser(self, company_email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(company_email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    # NOTE: AbstractBaseUser also implements two more fields:
    # password and last_login.
    name = models.CharField(
        _('name'),
        max_length=255,
        blank=True,
        null=True,  # serializer validation requires both null & default
        default='',
    )
    company_email = models.EmailField(
        _('company email'),
        unique=True
    )

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'
        ),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now,
    )

    terms_agreed = models.BooleanField(
        _('terms_agreed'),
        default=False
    )
    referrer = models.CharField(
        _('referrer'),
        max_length=255,
        blank=True,
        null=True,
        default='',  # serializer validation requires both null & default
    )

    confirmation_code = models.CharField(
        _('confirmation code'),
        max_length=255,
        blank=True,
        null=True,
        default=''
    )
    company_email_confirmed = models.BooleanField(
        _('company_email confirmed'),
        default=False,
        help_text=_(
            'Designates whether the user has confirmed company_email address.'
        ),
    )

    company = models.ForeignKey(Company, related_name='users', null=True)

    mobile_number = models.CharField(max_length=20)
    objects = UserManager()

    USERNAME_FIELD = 'company_email'
    REQUIRED_FIELDS = []  # company_email/password required by default

    def __str__(self):
        return self.company_email

    def get_full_name(self):
        # django method that must be implemented
        return self.name

    def get_short_name(self):
        # django method that must be implemented
        return self.name
