from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.postgres.fields import JSONField


class Company(models.Model):

    # NOTE: For various reasons owing to how django handles empty values
    # in strings and how DRF serializers handle validation,
    # blank=True, null=True and default='' were necessary to keep
    # behaviour consistent between not specifying a field and
    # specifying it as None
    name = models.CharField(max_length=255, blank=True, null=True, default='')
    number = models.CharField(max_length=8, validators=[MinLengthValidator(8)])
    website = models.URLField(max_length=255, blank=True, null=True, default='')
    description = models.TextField(blank=True, null=True, default='')
    aims = JSONField()
    logo = models.FileField(blank=True, null=True)

    def __str__(self):
        return self.name
