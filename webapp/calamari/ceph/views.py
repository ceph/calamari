import json
from collections import defaultdict
from django.contrib.auth.models import User
from django.http import Http404
from ceph.models import Cluster, ClusterSpace, ClusterHealth
from ceph.models import OSDDump
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

    @link()
    def health_counters(self, request, pk=None):
        cluster = self.get_object()
        osdump = OSDDump.objects.filter(cluster=cluster).latest()
        osd_counters = self._count_osds(osdump.report['osds'])
        return Response({
            'osd': osd_counters,
        })

    def _count_osds(self, osds):
        """
        Group and count OSDs by their status.
        """
        counts = defaultdict(lambda: 0)
        counts['total'] = len(osds)
        for osd in osds:
            up, inn = osd['up'], osd['in']
            if up and inn:
                counts['up_in'] += 1
            elif up and not inn:
                counts['up_not_in'] += 1
            elif not up and not inn:
                counts['not_up_not_in'] += 1
        return counts

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
