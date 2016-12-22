from django.contrib import admin
from django.conf.urls import url
from django.http import HttpResponse

from company.models import Company, CompanyCaseStudy


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified',)

    def get_urls(self):
        urls = super(CompanyAdmin, self).get_urls()
        additional_urls = [
            url(r'^publish/$', self.admin_site.admin_view(self.publish),
                name="company_company_publish"),
        ]
        return additional_urls + urls

    def publish(self, request):
        """Publish companies with the numbers defined in the POST request"""
        numbers = request.POST['company_numbers'].split(',')
        Company.objects.filter(number__in=numbers).update(is_published=True)
        return HttpResponse()


@admin.register(CompanyCaseStudy)
class CompanyCaseStudyAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified',)
