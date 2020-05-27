from django.db import models

from core.helpers import TimeStampedModel
from company.models import Company
from django.contrib.postgres.fields import JSONField

from directory_validators.string import no_html


class CompanyExportPlan(TimeStampedModel):

    company = models.ForeignKey(
        Company, related_name='company_export_plans', on_delete=models.CASCADE, blank=True, null=True
    )
    sso_id = models.PositiveIntegerField(verbose_name='sso user.sso_id', default=None, unique=False)
    export_countries = JSONField(blank=True, default=list)
    export_commodity_codes = JSONField(blank=True, default=list)
    rules_regulations = JSONField(null=True, blank=True, default=list)
    # business objectives
    rational = models.TextField(null=True, blank=True, default='', validators=[no_html])
    planned_review = models.TextField(null=True, blank=True, default='', validators=[no_html])
    # Target Markets
    sectors = JSONField(null=True, blank=True, default=list)
    consumer_demand = models.TextField(null=True, blank=True, default='', validators=[no_html])
    target_markets = JSONField(null=True, blank=True, default=list)
    # Adaptation for international markets
    compliance = JSONField(null=True, blank=True, default=list)
    export_certificates = JSONField(null=True, blank=True, default=list)
    # Marketing Approach
    route_to_markets = JSONField(null=True, blank=True, default=list)
    promotion_channels = JSONField(null=True, blank=True, default=list)
    resource_needed = models.TextField(null=True, blank=True, default='', validators=[no_html])
    spend_marketing = models.FloatField(null=True, default=None, unique=False)


class CompanyObjectives(TimeStampedModel):
    description = models.TextField(null=True, blank=True, default='', validators=[no_html])
    owner = models.PositiveIntegerField(null=True, verbose_name='sso user.sso_id', default=None, unique=False)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    companyexportplan = models.ForeignKey(
        CompanyExportPlan, related_name='company_objectives', on_delete=models.CASCADE
    )


class ExportPlanActions(TimeStampedModel):
    TARGET_MARKET_CHOICES = ('TARGET_MARKETS', 'Target Markets')
    owner = models.PositiveIntegerField(null=True, verbose_name='sso user.sso_id', default=None, unique=False)
    due_date = models.DateField(blank=True, null=True)
    is_reminders_on = models.BooleanField(default=False)
    action_type = models.CharField(max_length=15, choices=(TARGET_MARKET_CHOICES,), default=TARGET_MARKET_CHOICES[0])
    companyexportplan = models.ForeignKey(
        CompanyExportPlan, related_name='export_plan_actions', on_delete=models.CASCADE
    )
