from django.contrib import admin

from company.models import Company, CompanyCaseStudy


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified',)


@admin.register(CompanyCaseStudy)
class CompanyCaseStudyAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified',)
