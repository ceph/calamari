import json
from itertools import imap
from collections import defaultdict
from django.contrib.auth.models import User
from django.http import Http404
from django.utils import dateformat
from ceph.models import Cluster, ClusterSpace, ClusterHealth
from ceph.models import OSDDump, PGPoolDump
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
    def osd(self, request, pk=None):
        cluster = self.get_object()
        osdump = OSDDump.objects.filter(cluster=cluster).latest()
        return Response({
            'added': osdump.added,
            'added_ms': int(dateformat.format(osdump.added, 'U')) * 1000,
            'osds': osdump.report['osds'],
        })

    @link()
    def health_counters(self, request, pk=None):
        cluster = self.get_object()
        osdump = OSDDump.objects.filter(cluster=cluster).latest()
        pooldump = PGPoolDump.objects.filter(cluster=cluster).latest()
        oldest_update = min([osdump.added, pooldump.added])
        return Response({
            'added': oldest_update,
            'added_ms': int(dateformat.format(oldest_update, 'U')) * 1000,
            'osd': self._count_osds(osdump.report['osds']),
            'pool': self._count_pools(pooldump.report)
        })

    def _count_pools(self, pools):
        """
        Group and count pools by their status.
        """
        fields = ['num_objects_unfound', 'num_objects_missing_on_primary',
            'num_deep_scrub_errors', 'num_shallow_scrub_errors',
            'num_scrub_errors', 'num_objects_degraded']
        counts = defaultdict(lambda: 0)
        for pool in imap(lambda p: p['stat_sum'], pools):
            for key, value in pool.items():
                counts[key] += min(value, 1)
        for delkey in set(counts.keys()) - set(fields):
            del counts[delkey]
        counts['total'] = len(pools)
        return counts

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
