from rest_framework.permissions import BasePermission, SAFE_METHODS


class AlicePermission(BasePermission):
    """
    Allows a GET request to schema, and view-defined requests to everything
    else so long as they're authenticated.
    """

    def has_permission(self, request, view):

        if request.method in SAFE_METHODS:
            if hasattr(view, 'action') and view.action == "schema":
                return True

        # as IsAuthenticated permission
        if request.user and request.user.is_authenticated():
            return True

        return False
