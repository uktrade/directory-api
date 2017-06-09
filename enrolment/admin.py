from django.contrib import admin

from enrolment.models import Enrolment


@admin.register(Enrolment)
class EnrolmentAdmin(admin.ModelAdmin):
    search_fields = ('data', )
    readonly_fields = ('created', 'modified',)
