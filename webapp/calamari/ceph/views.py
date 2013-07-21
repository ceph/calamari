import json
from itertools import imap
from collections import defaultdict
from django.contrib.auth.models import User
from django.http import Http404
from django.utils import dateformat
from django.core.exceptions import ObjectDoesNotExist
from ceph.models import Cluster, ClusterSpace, ClusterHealth
from ceph.models import OSDDump, PGPoolDump
from ceph.serializers import ClusterSerializer
from ceph.serializers import ClusterSpaceSerializer
from ceph.serializers import ClusterHealthSerializer
from ceph.serializers import UserSerializer
from rest_framework import viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, link

class OSDList(APIView):
    model = OSDDump

    def get(self, request, cluster_pk):
        dump = OSDDump.objects.filter(cluster__pk=cluster_pk).latest()
        return Response({
            'added': dump.added,
            'added_ms': int(dateformat.format(dump.added, 'U')) * 1000,
            'osds': dump.report['osds'],
            'epoch': dump.pk,
        })

class OSDDetail(APIView):
    model = OSDDump

    def _get_osd(self, osds, id):
        for osd in osds:
            if osd['osd'] == int(id):
                return osd
        return None

    def get(self, request, cluster_pk, osd_id):
        dump = OSDDump.objects.filter(cluster__pk=cluster_pk).latest()
        osd = self._get_osd(dump.report['osds'], osd_id)
        if not osd:
            raise Http404
        return Response({
            'added': dump.added,
            'added_ms': int(dateformat.format(dump.added, 'U')) * 1000,
            'osd': osd,
        })

class OSDListDelta(APIView):
    model = OSDDump

    def _get_dump(self, cluster_pk, pk=None):
        dump = OSDDump.objects.filter(cluster__pk=cluster_pk)
        try:
            if pk:
                return dump.get(pk=pk)
            else:
                return dump.latest()
        except ObjectDoesNotExist:
            raise Http404

    def _osds_equal(self, a, b):
        """
        Simple single-level dictionary comparison.
        """
        if a.keys() != b.keys():
            return False
        for key, value in a.items():
            if b[key] != value:
                return False
        return True

    def _calc_delta(self, latest, old):
        # look-up table by osd-id
        old_by_id = {}
        for osd in old:
            old_by_id[osd['osd']] = osd

        # build the delta
        new, changed = [], []
        for osd in latest:
            id = osd['osd']
            if old_by_id.has_key(id):
                other = old_by_id[id]
                if not self._osds_equal(osd, other):
                    changed.append(osd)
                del old_by_id[id]
            else:
                new.append(osd)

        # new, removed, changed
        return new, old_by_id.values(), changed

    def get(self, request, cluster_pk, epoch):
        latest_dump = self._get_dump(cluster_pk)
        old_dump = self._get_dump(cluster_pk, epoch)
        new, removed, changed = self._calc_delta(
                latest_dump.report['osds'], old_dump.report['osds'])
        return Response({
            'added': latest_dump.added,
            'added_ms': int(dateformat.format(latest_dump.added, 'U')) * 1000,
            'new': new,
            'removed': removed,
            'changed': changed,
            'epoch': latest_dump.pk,
        })

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
