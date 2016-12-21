from django.contrib import admin

from company.models import Company, CompanyCaseStudy


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    search_fields = (
        'name', 'description', 'export_status', 'keywords', 'contact_details',
        'sectors', 'website', 'verification_code'
    )
    readonly_fields = ('created', 'modified',)


@admin.register(CompanyCaseStudy)
class CompanyCaseStudyAdmin(admin.ModelAdmin):
    search_fields = (
        'name', 'description', 'title', 'website', 'keywords', 'testimonial',
        'testimonial_company', 'testimonial_name',
    )
    readonly_fields = ('created', 'modified',)
