from django.contrib import admin

from enrolment.models import Enrolment


@admin.register(Enrolment)
class EnrolmentAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'modified',)
