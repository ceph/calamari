import json
from itertools import imap
from collections import defaultdict
from django.contrib.auth.models import User
from django.http import Http404
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
            'added_ms': dump.added_ms,
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
            'added_ms': dump.added_ms,
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
            'added_ms': latest_dump.added_ms,
            'new': new,
            'removed': removed,
            'changed': changed,
            'epoch': latest_dump.pk,
        })

class HealthCounters(APIView):
    model = Cluster

    def get(self, request, cluster_pk):
        osdump = OSDDump.objects.filter(cluster__pk=cluster_pk).latest()
        pooldump = PGPoolDump.objects.filter(cluster__pk=cluster_pk).latest()
        oldest_update = min([osdump, pooldump], key=lambda m: m.added)
        return Response({
            'added': oldest_update.added,
            'added_ms': oldest_update.added_ms,
            'osd': self._count_osds(osdump),
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

    def _count_osds(self, osdump):
        """
        Group and count OSDs by their status.
        """
        total, up_in, up_not_in, not_up_not_in = osdump.num_osds
        return {
            'total': total,
            'up_in': up_in,
            'up_not_in': up_not_in,
            'not_up_not_in': not_up_not_in,
        }

class Space(APIView):
    model = Cluster

    def get(self, request, cluster_pk):
        space = ClusterSpace.objects.filter(cluster__pk=cluster_pk).latest()
        return Response(ClusterSpaceSerializer(space).data)

class Health(APIView):
    model = Cluster

    def get(self, request, cluster_pk):
        health = ClusterHealth.objects.filter(cluster__pk=cluster_pk).latest()
        return Response(ClusterHealthSerializer(health).data)

class ClusterViewSet(viewsets.ModelViewSet):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
