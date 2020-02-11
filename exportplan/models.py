from django.db import models

from core.helpers import TimeStampedModel
from company.models import Company
from django.contrib.postgres.fields import JSONField


class CompanyExportPlan(TimeStampedModel):

    company = models.ForeignKey(
        Company, related_name='company_export_plans', on_delete=models.CASCADE, blank=True, null=True
    )
    sso_id = models.PositiveIntegerField(verbose_name='sso user.sso_id', default=None)
    export_countries = JSONField(blank=True, default=[])
    export_commodity_codes = JSONField(blank=True, default=[])
