from django.contrib.postgres.fields import ArrayField
from django.db import models

from core.helpers import TimeStampedModel


class Office(TimeStampedModel):
    class Meta:
        ordering = ['region_id']

    id = models.AutoField(auto_created=True, primary_key=True)
    region_id = models.TextField(blank=True, null=True)
    region_ids = ArrayField(models.TextField(), null=True, help_text='Regions need to be separated by commas.')
    name = models.TextField()
    address_street = models.TextField()
    address_city = models.TextField()
    address_postcode = models.TextField()
    email = models.EmailField()
    phone = models.TextField()
    phone_other = models.TextField(blank=True, null=True)
    phone_other_comment = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    override_office_details = models.TextField(
        blank=True,
        null=True,
        help_text=(
            'If this field has a value all fields above will be ignored and the details in this field will be displayed'
            '. Other office details will not be displayed if this is the main search result.'
            ' If this office is in the results page of other offices, this will be the details displayed.'
        ),
    )
    order = models.IntegerField(blank=True, null=True)


class Postcode(TimeStampedModel):
    class Meta:
        indexes = [
            models.Index(
                fields=[
                    'post_code',
                ]
            ),
        ]
        ordering = ['post_code', 'region', 'european_electoral_region']

    post_code = models.TextField(blank=False, null=False)
    region = models.TextField(blank=True, null=True)
    european_electoral_region = models.TextField(blank=True, null=True)
