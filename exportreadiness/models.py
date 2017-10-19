from django.db import models

from directory_constants.constants import exred_sector_names
from django.utils.functional import cached_property

from api.model_utils import TimeStampedModel


class TriageResult(TimeStampedModel):
    sector = models.CharField(
        choices=exred_sector_names.SECTORS_CHOICES,
        max_length=255
    )
    exported_before = models.BooleanField()
    regular_exporter = models.BooleanField()
    used_online_marketplace = models.BooleanField()
    company_name = models.CharField(max_length=255, null=True, blank=True)
    sole_trader = models.BooleanField()
    sso_id = models.PositiveIntegerField(unique=True)

    @cached_property
    def sector_name(self):
        return exred_sector_names.CODES_SECTORS_DICT[self.sector]

    def __str__(self):  # pragma: no cover
        return self.company_name
