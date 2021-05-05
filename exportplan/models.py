from directory_constants import choices
from directory_validators.string import no_html
from django.contrib.postgres.fields import JSONField
from django.db import models

from company.models import Company
from core.helpers import TimeStampedModel, path_and_rename_exportplan_pdf
from core.storage import PrivateMediaStorage


class CompanyExportPlan(TimeStampedModel):

    # General fields

    company = models.ForeignKey(
        Company, related_name='company_export_plans', on_delete=models.CASCADE, blank=True, null=True
    )
    sso_id = models.PositiveIntegerField(verbose_name='sso user.sso_id', default=None, unique=False)
    export_countries = JSONField(blank=True, default=list)
    export_commodity_codes = JSONField(blank=True, default=list)
    ui_options = JSONField(null=True, blank=True, default=dict)
    ui_progress = JSONField(null=True, blank=True, default=dict)

    about_your_business = JSONField(null=True, blank=True, default=dict)
    # business objectives
    objectives = JSONField(null=True, blank=True, default=dict)
    # Target Markets Research
    target_markets_research = JSONField(null=True, blank=True, default=dict)
    # Target Markets
    sectors = JSONField(null=True, blank=True, default=list)
    target_markets = JSONField(null=True, blank=True, default=dict)
    # adaptation for your target target
    adaptation_target_market = JSONField(null=True, blank=True, default=dict)
    # Marketing Approach
    marketing_approach = JSONField(null=True, blank=True, default=dict)
    # Cost and Pricing
    direct_costs = JSONField(null=True, blank=True, default=dict)
    overhead_costs = JSONField(null=True, blank=True, default=dict)
    total_cost_and_price = JSONField(null=True, blank=True, default=dict)
    # Funding and Credit
    funding_and_credit = JSONField(null=True, blank=True, default=dict)
    # Getting paid
    getting_paid = JSONField(null=True, blank=True, default=dict)
    # Travel Business Policies
    travel_business_policies = JSONField(null=True, blank=True, default=dict)


class CompanyObjectives(TimeStampedModel):
    description = models.TextField(null=True, blank=True, default='', validators=[no_html])
    planned_reviews = models.TextField(blank=True, default='', validators=[no_html])
    owner = models.TextField(null=True, blank=True, max_length=100)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    companyexportplan = models.ForeignKey(
        CompanyExportPlan, related_name='company_objectives', on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = "Company Objectives"


class ExportplanDownloads(TimeStampedModel):
    pdf_file = models.FileField(
        upload_to=path_and_rename_exportplan_pdf, storage=PrivateMediaStorage(), blank=False, null=False
    )
    companyexportplan = models.ForeignKey(
        CompanyExportPlan, related_name='exportplan_downloads', on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = "Exportplan downloads"


class RouteToMarkets(TimeStampedModel):
    route = models.CharField(max_length=30, blank=True, null=True, default='', choices=choices.MARKET_ROUTE_CHOICES)
    promote = models.CharField(
        max_length=30, blank=True, null=True, default='', choices=choices.PRODUCT_PROMOTIONAL_CHOICES
    )
    market_promotional_channel = models.TextField(blank=True, default='', validators=[no_html])

    companyexportplan = models.ForeignKey(CompanyExportPlan, related_name='route_to_markets', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Route To Markets"


class ExportPlanActions(TimeStampedModel):
    TARGET_MARKET_CHOICES = ('TARGET_MARKETS', 'Target Markets')
    owner = models.PositiveIntegerField(null=True, verbose_name='sso user.sso_id', default=None, unique=False)
    due_date = models.DateField(blank=True, null=True)
    is_reminders_on = models.BooleanField(default=False)
    action_type = models.CharField(max_length=15, choices=(TARGET_MARKET_CHOICES,), default=TARGET_MARKET_CHOICES[0])
    companyexportplan = models.ForeignKey(
        CompanyExportPlan, related_name='export_plan_actions', on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = "Export Plan Actions"


class TargetMarketDocuments(TimeStampedModel):
    document_name = models.TextField(blank=True, default='', validators=[no_html])
    note = models.TextField(blank=True, default='', validators=[no_html])

    companyexportplan = models.ForeignKey(
        CompanyExportPlan, related_name='target_market_documents', on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = "Target Market Documents"


class FundingCreditOptions(TimeStampedModel):
    funding_option = models.CharField(max_length=30, blank=True, null=True, default='', choices=choices.FUNDING_OPTIONS)
    amount = models.FloatField(blank=True, null=True)
    companyexportplan = models.ForeignKey(
        CompanyExportPlan, related_name='funding_credit_options', on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = "Funding Credit Options"


class BusinessTrips(TimeStampedModel):
    note = models.TextField(blank=True, default='', validators=[no_html])
    companyexportplan = models.ForeignKey(CompanyExportPlan, related_name='business_trips', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Business Trips"


class BusinessRisks(TimeStampedModel):
    risk = models.TextField(blank=True, default='', validators=[no_html])
    contingency_plan = models.TextField(blank=True, default='', validators=[no_html])
    risk_likelihood = models.CharField(
        max_length=30, blank=True, null=True, default='', choices=choices.RISK_LIKELIHOOD_OPTIONS
    )
    risk_impact = models.CharField(
        max_length=30, blank=True, null=True, default='', choices=choices.RISK_IMPACT_OPTIONS
    )
    companyexportplan = models.ForeignKey(CompanyExportPlan, related_name='business_risks', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Business Risks"
