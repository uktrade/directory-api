from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser):

    # NOTE: AbstractBaseUser also implements two more fields:
    # password and last_login.
    name = models.CharField(
        _('name'),
        max_length=255,
        blank=True,
        null=True,  # serializer validation requires both null & default
        default='',
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
    is_superuser = models.BooleanField(
        _('superuser status'),
        default=False,
        help_text=_('Designates whether the user '
                    'has superuser privileges.'),
    )
    terms_agreed = models.BooleanField(_('terms_agreed'), default=False)
    referrer = models.CharField(
        _('referrer'),
        max_length=255,
        blank=True,
        null=True,
        default='',  # serializer validation requires both null & default
    )

    objects = UserManager()

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
