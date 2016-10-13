from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.postgres.fields import JSONField


class Company(models.Model):

    name = models.CharField(max_length=255, blank=True)
    number = models.CharField(max_length=8, validators=[MinLengthValidator(8)])
    website = models.URLField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    aims = JSONField()
    logo = models.FileField(blank=True, null=True)

    def __str__(self):
        return self.name
