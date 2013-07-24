import json
from itertools import imap
from collections import defaultdict
from django.contrib.auth.models import User
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from ceph.models import Cluster, ClusterSpace, ClusterHealth
from ceph.models import OSDDump, PGPoolDump, ClusterStatus
from ceph.serializers import ClusterSerializer
from ceph.serializers import ClusterSpaceSerializer
from ceph.serializers import ClusterHealthSerializer
from ceph.serializers import UserSerializer
from rest_framework import viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, link

class StampedResponse(Response):
    """
    A rest_framework Response with uniform treatment of timestamps.

    Args:
      dateobj: the Dump model to take time information from
      data: the dictionary all the context-dependent values
    """
    def __init__(self, dateobj, data, *args, **kwargs):
        data.update({'added': dateobj.added, 'added_ms': dateobj.added_ms})
        super(StampedResponse, self).__init__(data, *args, **kwargs)

class OSDList(APIView):
    """
    Access to the list of OSDs in a cluster.
    """
    model = OSDDump

    def get(self, request, cluster_pk):
        "Return the latest list of OSDs"
        dump = OSDDump.objects.for_cluster(cluster_pk).latest()
        return StampedResponse(dump, {
            'osds': dump.osds,
            'epoch': dump.pk,
        })

class OSDDetail(APIView):
    """
    Access details of a single OSD.
    """
    model = OSDDump

    def get(self, request, cluster_pk, osd_id):
        "Return detail of OSD identified by osd_id"
        dump = OSDDump.objects.for_cluster(cluster_pk).latest()
        osd = dump.get_osd(osd_id)
        if not osd:
            raise Http404
        return StampedResponse(dump, {'osd': osd})

class OSDListDelta(APIView):
    """
    Return list of OSDs that have changed since a point in the past.
    """
    model = OSDDump

    def _get_spread(self, cluster_pk, epoch):
        "Returns the latest and a specific OSD state dump"
        all = OSDDump.objects.for_cluster(cluster_pk)
        try:
            return all.latest(), all.get(pk=epoch)
        except OSDDump.DoesNotExist:
            raise Http404()

    def get(self, request, cluster_pk, epoch):
        """
        Return the OSD list delta since epoch (i.e. a primary-key).
        """
        current, past = self._get_spread(cluster_pk, epoch)
        new, removed, changed = current.delta(past)
        return StampedResponse(current, {
            'new': new,
            'removed': removed,
            'changed': changed,
            'epoch': current.pk,
        })

class HealthCounters(APIView):
    model = Cluster

    def get(self, request, cluster_pk):
        pooldump = PGPoolDump.objects.for_cluster(cluster_pk).latest()
        status = ClusterStatus.objects.for_cluster(cluster_pk).latest()
        oldest_update = min([pooldump, status], key=lambda m: m.added)
        return StampedResponse(oldest_update, {
            'osd': self._count_osds(status),
            'pool': self._count_pools(pooldump.report),
            'mds': self._count_mds(status),
            'mon': self._count_mon(status),
            'pg': self._count_pg(status),
        })

    def _count_pg(self, status):
        total, ok, warn, crit = status.pg_count_by_status()
        return {
            'total': total,
            'ok': ok,
            'warn': warn,
            'critical': crit,
        }

    def _count_mon(self, status):
        total, in_quorum, not_in_quorum = status.mon_count_by_status()
        return {
            'total': total,
            'in_quorum': in_quorum,
            'not_in_quorum': not_in_quorum,
        }

    def _count_mds(self, status):
        total, up_in, up_nin, nup_nin = status.mds_count_by_status()
        return {
            'total': total,
            'up_in': up_in,
            'up_not_in': up_nin,
            'not_up_not_in': nup_nin,
        }

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

    def _count_osds(self, status):
        """
        Group and count OSDs by their status.
        """
        total, up_in, up_nin, nup_nin = status.osd_count_by_status()
        return {
            'total': total,
            'up_in': up_in,
            'up_not_in': up_nin,
            'not_up_not_in': nup_nin,
        }

class Space(APIView):
    model = Cluster

    def get(self, request, cluster_pk):
        space = ClusterSpace.objects.for_cluster(cluster_pk).latest()
        return Response(ClusterSpaceSerializer(space).data)

class Health(APIView):
    model = Cluster

    def get(self, request, cluster_pk):
        health = ClusterHealth.objects.for_cluster(cluster_pk).latest()
        return Response(ClusterHealthSerializer(health).data)

class ClusterViewSet(viewsets.ModelViewSet):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
