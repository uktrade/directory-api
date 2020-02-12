from django.db import models

from core.helpers import TimeStampedModel


class UserLocation(TimeStampedModel):
    sso_id = models.PositiveIntegerField(verbose_name='sso user.sso_id', default=None)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    region = models.TextField()
    country = models.TextField()
