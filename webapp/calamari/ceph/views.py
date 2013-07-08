from django.contrib.auth.models import User
from django.http import Http404
from ceph.models import Cluster, ClusterSpace
from ceph.serializers import UserSerializer, ClusterSerializer, ClusterSpaceSerializer
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, link

class ClusterViewSet(viewsets.ModelViewSet):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer

    @link()
    def space(self, request, pk=None):
        cluster = self.get_object()
        space = ClusterSpace.objects.filter(cluster=cluster).latest()
        return Response(ClusterSpaceSerializer(space).data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
