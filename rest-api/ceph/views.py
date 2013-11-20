
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework import status

from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User

from ceph.serializers import ClusterSpaceSerializer, ClusterHealthSerializer, UserSerializer,\
    ClusterSerializer, OSDDetailSerializer, OSDListSerializer, ClusterHealthCountersSerializer, OSDMapSerializer, PoolSerializer, RequestSerializer

import zerorpc
from zerorpc.exceptions import LostRemote
from cthulhu.manager.rpc import CTHULHU_RPC_URL

import pytz

from graphite.render.attime import parseATTime
from graphite.render.datalib import fetchData


def get_latest_graphite(metric):
    """
    Get the latest value of a named graphite metric
    """

    tzinfo = pytz.timezone("UTC")
    until_time = parseATTime('now', tzinfo)
    from_time = parseATTime('-10min', tzinfo)
    series = fetchData({
        'startTime': from_time,
        'endTime': until_time,
        'localOnly': False},
        metric
    )
    try:
        return [k for k in series[0] if k is not None][-1]
    except IndexError:
        return None


class DataObject(object):
    """
    A convenience for converting dicts from the backend into
    objects, because django_rest_framework expects objects
    """
    def __init__(self, data):
        self.__dict__.update(data)


class RPCView(APIView):
    def __init__(self, *args, **kwargs):
        super(RPCView, self).__init__(*args, **kwargs)
        self.client = zerorpc.Client()
        self.client.connect(CTHULHU_RPC_URL)

    def handle_exception(self, exc):
        try:
            return super(RPCView, self).handle_exception(exc)
        except LostRemote as e:
            return Response({'detail': "RPC error ('%s')" % e},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE, exception=True)


class Space(RPCView):
    def get(self, request, fsid):
        def to_bytes(kb):
            if kb is not None:
                return kb * 1024
            else:
                return None

        cluster = self.client.get_cluster(fsid)

        df_path = lambda stat_name: "ceph.{0}.df.{1}".format(cluster['name'], stat_name)
        space = {
            'used_bytes': to_bytes(get_latest_graphite(df_path('total_used'))),
            'capacity_bytes': to_bytes(get_latest_graphite(df_path('total_space'))),
            'free_bytes': to_bytes(get_latest_graphite(df_path('totaL_avail')))
        }

        return Response(ClusterSpaceSerializer(DataObject({
            'space': space
        })).data)


class Health(RPCView):
    def get(self, request, fsid):
        health = self.client.get_sync_object(fsid, 'health')
        return Response(ClusterHealthSerializer(DataObject({
            'report': health,
            'cluster_update_time': self.client.get_cluster(fsid)['update_time']
        })).data)


class HealthCounters(RPCView):
    def get(self, request, fsid):
        counters = self.client.get_derived_object(fsid, 'counters')
        if not counters:
            return Response({}, status.HTTP_202_ACCEPTED)

        return Response(ClusterHealthCountersSerializer(DataObject({
            'counters': counters,
            'cluster_update_time': self.client.get_cluster(fsid)['update_time']
        })).data)


class OSDList(RPCView):
    def _filter_by_pg_state(self, osds, pg_states, osds_by_pg_state):
        """Filter the cluster OSDs by PG states.

        Note that we can't do any nice DB querying here because we aren't
        normalizing out our data to fit the relational model. Thus, this is a
        bit hacky.

        We are modifying the OSD field of this instance of a cluster based on
        the filtering, and passing the result to the serializer. Do not do
        anything like a .save() on this instance; it's just a vehicle for the
        filtered OSDs.
        """
        pg_states = set(map(lambda s: s.lower(), pg_states.split(",")))
        target_osds = set([])
        for state, osds in osds_by_pg_state.iteritems():
            if state in pg_states:
                target_osds |= set(osds)
        return [o for o in osds if o['id'] in target_osds]

    def get(self, request, fsid):
        osds = self.client.get_derived_object(fsid, 'osds')
        osds_by_pg_state = self.client.get_derived_object(fsid, 'osds_by_pg_state')
        if not osds or not osds_by_pg_state:
            return Response([], status.HTTP_202_ACCEPTED)

        pg_states = request.QUERY_PARAMS.get('pg_states', None)
        if pg_states:
            self._filter_by_pg_state(osds, pg_states, osds_by_pg_state)

        osd_list = DataObject({
            #'osds': [DataObject({'osd': o}) for o in osds],
            'osds': osds,
            'osds_by_pg_state': osds_by_pg_state
        })

        return Response(OSDListSerializer(osd_list).data)


class OSDDetail(RPCView):
    def get(self, request, fsid, osd_id):
        data = self.client.get(fsid, 'osd', int(osd_id))
        osd = DataObject({'osd': data})
        return Response(OSDDetailSerializer(osd).data)


class OSDMap(RPCView):
    def get(self, request, fsid):
        data = self.client.get_sync_object(fsid, 'osd_map')
        osd_map = DataObject({'version': data['epoch'], 'data': data})
        return Response(OSDMapSerializer(osd_map).data)


class RPCViewSet(viewsets.ViewSetMixin, RPCView):
    pass


class ClusterViewSet(RPCViewSet):
    def list(self, request):
        clusters = [DataObject(c) for c in self.client.list_clusters()]

        return Response(ClusterSerializer(clusters, many=True).data)

    def retrieve(self, request, pk):
        cluster = DataObject(self.client.get_cluster(pk))
        return Response(ClusterSerializer(cluster).data)

    def delete(self, request, pk):
        self.client.delete_cluster(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PoolViewSet(RPCViewSet):
    def list(self, request, fsid):
        pools = [DataObject(p) for p in self.client.list(fsid, 'pool')]

        return Response(PoolSerializer(pools, many=True).data)

    def retrieve(self, request, fsid, pool_id):
        pool = DataObject(self.client.get(fsid, 'pool', int(pool_id)))
        return Response(PoolSerializer(pool).data)

    def create(self, request, fsid):
        serializer = PoolSerializer(data=request.DATA)
        if serializer.is_valid():
            create_response = self.client.create(fsid, 'pool', request.DATA)
            # TODO: handle case where the creation is rejected for some reason (should
            # be passed an errors dict for a clean failure, or a zerorpc exception
            # for a dirty failure)
            assert 'request_id' in create_response
            return Response(create_response)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, fsid, pool_id):
        delete_response = self.client.delete(fsid, 'pool', int(pool_id))
        return Response(delete_response)

    def update(self, request, fsid, pool_id):
        updates = request.DATA
        print updates
        # TODO: validation, but we don't want to check all fields are present (because
        # this is a PATCH), just that those present are valid.  rest_framework serializer
        # may or may not be able to do that out the box.
        return Response(self.client.update(fsid, 'pool', int(pool_id), updates))


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RequestViewSet(RPCViewSet):
    def retrieve(self, request, fsid, request_id):
        user_request = DataObject(self.client.get_request(fsid, request_id))
        return Response(RequestSerializer(user_request).data)


@api_view(['GET'])
@permission_classes((AllowAny,))
@never_cache
def user_me(request):
    """
    Return information about the current user. If the user is not authenticated
    (i.e. an anonymous user), then 401 is returned with an error message.
    """
    if request.method != 'GET':
        return
    if request.user.is_authenticated():
        return Response(UserSerializer(request.user).data)
    return Response({
        'message': 'Session expired or invalid',
    }, status.HTTP_401_UNAUTHORIZED)
