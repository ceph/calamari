import json
from django.contrib.auth.models import User
from django.http import Http404
from ceph.models import Cluster, ClusterSpace, ClusterHealth
from ceph.serializers import ClusterSerializer
from ceph.serializers import ClusterSpaceSerializer
from ceph.serializers import ClusterHealthSerializer
from ceph.serializers import UserSerializer
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

    @link()
    def health(self, request, pk=None):
        cluster = self.get_object()
        health = ClusterHealth.objects.filter(cluster=cluster).latest()
        return Response(ClusterHealthSerializer(health).data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
