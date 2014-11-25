from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet

from calamari_rest.permissions import IsRoleAllowed


class RoleLimitedViewSet(ViewSet):
    permission_classes = [IsAuthenticated, IsRoleAllowed]
