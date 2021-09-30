from rest_framework import permissions

from exportplan.models import CompanyExportPlan


class IsExportPlanOwner(permissions.BasePermission):
    """
    Allows access only to a user who owns the export plan.
    """

    def has_permission(self, request, view):
        get_id = view.kwargs.get('pk') or request.data.get('companyexportplan')
        export_plan = CompanyExportPlan.objects.get(pk=get_id)
        return export_plan.sso_id == request.user.id
