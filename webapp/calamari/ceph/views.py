from django.contrib.auth.models import User
from django.http import Http404
from ceph.models import Cluster
from ceph.serializers import UserSerializer, ClusterSerializer
from rest_framework import viewsets
from rest_framework.response import Response

class ClusterViewSet(viewsets.ModelViewSet):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
