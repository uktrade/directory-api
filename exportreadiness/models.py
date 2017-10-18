from django.db import models


from api.model_utils import TimeStampedModel


class TriageResult(TimeStampedModel):
    sector = models.CharField(max_length=255)
    exported_before = models.BooleanField()
    exporting_regular_part = models.BooleanField()
    company_name = models.CharField(max_length=100)
    sole_trader = models.BooleanField()
    sso_id = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return self.company_name
