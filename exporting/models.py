from core.helpers import TimeStampedModel
from django.db import models


class Office(TimeStampedModel):
    region_id = models.TextField(primary_key=True)
    address_street = models.TextField()
    address_city = models.TextField()
    address_postcode = models.TextField()
    email = models.EmailField()
    phone = models.TextField()
