from directory_constants import choices
from directory_validators.string import no_html
from django.contrib.postgres.fields import JSONField
from django.db import models

from company.models import Company
from core.helpers import TimeStampedModel


class CompanyExportPlan(TimeStampedModel):

    # General fields

    company = models.ForeignKey(
        Company, related_name='company_export_plans', on_delete=models.CASCADE, blank=True, null=True
    )
    sso_id = models.PositiveIntegerField(verbose_name='sso user.sso_id', default=None, unique=False)
    export_countries = JSONField(blank=True, default=list)
    export_commodity_codes = JSONField(blank=True, default=list)
    ui_options = JSONField(null=True, blank=True, default=dict)

    about_your_business = JSONField(null=True, blank=True, default=dict)
    # business objectives
    objectives = JSONField(null=True, blank=True, default=list)
    # Target Markets Research
    target_markets_research = JSONField(null=True, blank=True, default=dict)
    # Target Markets
    sectors = JSONField(null=True, blank=True, default=list)
    consumer_demand = models.TextField(null=True, blank=True, default='', validators=[no_html])
    target_markets = JSONField(null=True, blank=True, default=list)
    # Adaptation for international markets
    compliance = JSONField(null=True, blank=True, default=list)
    export_certificates = JSONField(null=True, blank=True, default=list)
    # adaptation for your target target
    adaptation_target_market = JSONField(null=True, blank=True, default=list)
    # Marketing Approach
    marketing_approach = JSONField(null=True, blank=True, default=list)
    promotion_channels = JSONField(null=True, blank=True, default=list)
    resource_needed = models.TextField(null=True, blank=True, default='', validators=[no_html])
    spend_marketing = models.FloatField(null=True, default=None, unique=False)


class CompanyObjectives(TimeStampedModel):
    description = models.TextField(null=True, blank=True, default='', validators=[no_html])
    planned_reviews = models.TextField(blank=True, default='', validators=[no_html])
    owner = models.TextField(null=True, blank=True, max_length=100)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    companyexportplan = models.ForeignKey(
        CompanyExportPlan, related_name='company_objectives', on_delete=models.CASCADE
    )


class RouteToMarkets(TimeStampedModel):
    route = models.CharField(max_length=30, blank=True, null=True, default='', choices=choices.MARKET_ROUTE_CHOICES)
    promote = models.CharField(
        max_length=30, blank=True, null=True, default='', choices=choices.PRODUCT_PROMOTIONAL_CHOICES
    )
    market_promotional_channel = models.TextField(blank=True, default='', validators=[no_html])

    companyexportplan = models.ForeignKey(CompanyExportPlan, related_name='route_to_markets', on_delete=models.CASCADE)


class ExportPlanActions(TimeStampedModel):
    TARGET_MARKET_CHOICES = ('TARGET_MARKETS', 'Target Markets')
    owner = models.PositiveIntegerField(null=True, verbose_name='sso user.sso_id', default=None, unique=False)
    due_date = models.DateField(blank=True, null=True)
    is_reminders_on = models.BooleanField(default=False)
    action_type = models.CharField(max_length=15, choices=(TARGET_MARKET_CHOICES,), default=TARGET_MARKET_CHOICES[0])
    companyexportplan = models.ForeignKey(
        CompanyExportPlan, related_name='export_plan_actions', on_delete=models.CASCADE
    )


class TargetMarketDocuments(TimeStampedModel):
    document_name = models.TextField(blank=True, default='', validators=[no_html])
    note = models.TextField(blank=True, default='', validators=[no_html])

    companyexportplan = models.ForeignKey(
        CompanyExportPlan, related_name='target_market_documents', on_delete=models.CASCADE
    )
