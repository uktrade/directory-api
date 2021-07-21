from django.db import models

from core.helpers import TimeStampedModel
from django.contrib.postgres.fields import JSONField


class UserLocation(TimeStampedModel):
    sso_id = models.PositiveIntegerField(verbose_name='sso user.sso_id', default=None)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    region = models.TextField()
    country = models.TextField()
    city = models.TextField()


class CountryOfInterest(TimeStampedModel):
    country = models.TextField()
    sector = models.TextField()
    service = models.TextField()


class BusinessUser(TimeStampedModel):
    sso_id = models.PositiveIntegerField(verbose_name='sso user.sso_id', primary_key=True)


class UserMarket(TimeStampedModel):
    business_user = models.ForeignKey(BusinessUser, on_delete=models.CASCADE)
    country_iso2_code = models.CharField(max_length=10)
    data = JSONField(null=True, blank=True, default=dict)


class UserProduct(TimeStampedModel):
    business_user = models.ForeignKey(BusinessUser, on_delete=models.CASCADE)
    product_data = JSONField(blank=True, default=list)

