from django.db import models
from django.utils.translation import gettext as _

from core.helpers import TimeStampedModel


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


class SuggestedCountry(TimeStampedModel):
    hs_code = models.PositiveIntegerField(_('HS Code'))
    country = models.ForeignKey('dataservices.Country',
        verbose_name=_('Suggested Countries'),
        on_delete=models.SET_NULL,
        null=True
        )
    order = models.PositiveIntegerField(_('Order'), null=True, blank=True)

    def __str__(self):
        return str(self.hs_code)

    class Meta:
        verbose_name = 'Suggested Country'
        verbose_name_plural = 'Suggested Countries'
