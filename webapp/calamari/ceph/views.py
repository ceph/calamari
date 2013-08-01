import json
from itertools import imap
from collections import defaultdict
from django.contrib.auth.models import User
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from ceph.models import Cluster
from ceph.serializers import *
from rest_framework import viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, link
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework import status
from django.views.decorators.cache import never_cache

class Space(APIView):
    model = Cluster

    def get(self, request, cluster_pk):
        cluster = Cluster.objects.get(pk=cluster_pk)
        if not cluster.space:
            return Response({}, status.HTTP_404_NOT_FOUND)
        return Response(ClusterSpaceSerializer(cluster).data)

class Health(APIView):
    model = Cluster

    def get(self, request, cluster_pk):
        cluster = Cluster.objects.get(pk=cluster_pk)
        if not cluster.health:
            return Response({}, status.HTTP_404_NOT_FOUND)
        return Response(ClusterHealthSerializer(cluster).data)

class OSDList(APIView):
    model = Cluster

    def get(self, request, cluster_pk):
        cluster = Cluster.objects.get(pk=cluster_pk)
        if not cluster.health:
            return Response({}, status.HTTP_404_NOT_FOUND)
        return Response(OSDListSerializer(cluster).data)

class OSDDetail(APIView):
    model = Cluster

    def get(self, request, cluster_pk, osd_id):
        cluster = Cluster.objects.get(pk=cluster_pk)
        if not cluster.has_osd(osd_id):
            return Response({}, status.HTTP_404_NOT_FOUND)
        return Response(OSDDetailSerializer(cluster, osd_id).data)

class ClusterViewSet(viewsets.ModelViewSet):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

#
# Return information about the current user. If the user is not authenticated
# (i.e. an anonymous user), then 401 is returned with an error message.
#
@api_view(['GET'])
@permission_classes((AllowAny,))
@never_cache
def user_me(request):
    if request.method != 'GET':
        return
    if request.user.is_authenticated():
        return Response(UserSerializer(request.user).data)
    return Response({
        'message': 'Session expired or invalid',
    }, status.HTTP_401_UNAUTHORIZED)
