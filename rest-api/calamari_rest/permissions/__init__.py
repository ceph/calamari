from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsRoleAllowed(BasePermission):

    def has_permission(self, request, view):
        has_permission = False
        if request.user.groups.filter(name='readonly').exists():
            has_permission = request.method in SAFE_METHODS
            view.headers['Allow'] = ', '.join(SAFE_METHODS)
        elif request.user.groups.filter(name='read/write').exists():
            has_permission = True
        elif request.user.is_superuser:
            has_permission = True

        return has_permission
