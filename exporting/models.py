from core.helpers import TimeStampedModel
from django.db import models


class Office(TimeStampedModel):
    class Meta:
        ordering = ['region_id']

    region_id = models.TextField(primary_key=True)
    name = models.TextField()
    address_street = models.TextField()
    address_city = models.TextField()
    address_postcode = models.TextField()
    email = models.EmailField()
    phone = models.TextField()
    phone_other = models.TextField(blank=True, null=True)
    phone_other_comment = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
