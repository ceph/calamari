
import logging
from django.core.urlresolvers import reverse
import pytz
import socket

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.models import User
from rest_framework.views import APIView

from calamari_rest.serializers.v1 import ClusterSpaceSerializer, ClusterHealthSerializer, UserSerializer, \
    ClusterSerializer, OSDDetailSerializer, OSDListSerializer, ClusterHealthCountersSerializer, \
    PoolSerializer, ServerSerializer, InfoSerializer

from salt.config import master_config
from salt.loader import _create_loader

from graphite.render.attime import parseATTime
from graphite.render.datalib import fetchData
from calamari_rest.views.rpc_view import RPCView, DataObject, RPCViewSet
from cthulhu.manager.types import POOL


from cthulhu.config import CalamariConfig
config = CalamariConfig()

log = logging.getLogger('django.request')


def get_latest_graphite(metric):
    """
    Get the latest value of a named graphite metric
    """

    tzinfo = pytz.timezone("UTC")
    until_time = parseATTime('now', tzinfo)

    def _get(from_time):
        series = fetchData({
            'startTime': from_time,
            'endTime': until_time,
            'now': until_time,
            'localOnly': False},
            metric
        )
        try:
            return [k for k in series[0] if k is not None][-1]
        except IndexError:
            return None

    # In case the cluster has been offline for some time, try looking progressively
    # further back in time for data.  This would not be necessary if graphite simply
    # let us ask for the latest value (Calamari issue #6876)
    for trange in ['-1min', '-10min', '-60min', '-1d', '-7d']:
        val = _get(parseATTime(trange, tzinfo))
        if val is not None:
            return val

    log.warn("No graphite data for %s" % metric)


class Space(RPCView):
    serializer_class = ClusterSpaceSerializer

    def get(self, request, fsid):
        def to_bytes(kb):
            if kb is not None:
                return kb * 1024
            else:
                return None

        #df_path = lambda stat_name: "ceph.cluster.{0}.df.{1}".format(fsid, stat_name)
        # TODO: Change names to FSIDs for #6883
        df_path = lambda stat_name: "ceph.cluster.{0}.df.{1}".format(self.client.get_cluster(fsid)['name'], stat_name)
        space = {
            'used_bytes': to_bytes(get_latest_graphite(df_path('total_used'))),
            'capacity_bytes': to_bytes(get_latest_graphite(df_path('total_space'))),
            'free_bytes': to_bytes(get_latest_graphite(df_path('total_avail')))
        }

        return Response(ClusterSpaceSerializer(DataObject({
            'space': space
        })).data)


class Health(RPCView):
    serializer_class = ClusterHealthSerializer

    def get(self, request, fsid):
        health = self.client.get_sync_object(fsid, 'health')
        return Response(ClusterHealthSerializer(DataObject({
            'report': health,
            'cluster_update_time': self.client.get_cluster(fsid)['update_time'],
            'cluster_update_time_unix': self.client.get_cluster(fsid)['update_time'],
        })).data)


class HealthCounters(RPCView):
    serializer_class = ClusterHealthCountersSerializer

    def get(self, request, fsid):
        counters = self.client.get_derived_object(fsid, 'counters')
        if not counters:
            return Response({}, status.HTTP_202_ACCEPTED)

        return Response(ClusterHealthCountersSerializer(DataObject({
            'counters': counters,
            'cluster_update_time': self.client.get_cluster(fsid)['update_time']
        })).data)


class OSDList(RPCView):
    """
    Provides an object which includes a list of all OSDs, and
    some summary counters (pg_state_counts)
    """
    serializer_class = OSDListSerializer

    def _filter_by_pg_state(self, osds, pg_states, osds_by_pg_state):
        """Filter the cluster OSDs by PG states.
`
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
        for state, state_osds in osds_by_pg_state.iteritems():
            if state in pg_states:
                target_osds |= set(state_osds)
        return [o for o in osds if o['id'] in target_osds]

    def get(self, request, fsid):
        osds = self.client.get_derived_object(fsid, 'osds')
        osds_by_pg_state = self.client.get_derived_object(fsid, 'osds_by_pg_state')
        if not osds or not osds_by_pg_state:
            return Response([], status.HTTP_202_ACCEPTED)

        pg_states = request.QUERY_PARAMS.get('pg_states', None)
        if pg_states:
            osds = self._filter_by_pg_state(osds, pg_states, osds_by_pg_state)

        osd_list = DataObject({
            #'osds': [DataObject({'osd': o}) for o in osds],
            'osds': osds,
            'osds_by_pg_state': osds_by_pg_state
        })

        return Response(OSDListSerializer(osd_list).data)


class OSDDetail(RPCView):
    """
    This is the same data that is provided in the OSD list, but for
    a single OSD, and not including the pg_state_counts.
    """
    serializer_class = OSDDetailSerializer

    def get(self, request, fsid, osd_id):
        data = self.client.get(fsid, 'osd', int(osd_id))
        osd = DataObject({'osd': data})
        return Response(OSDDetailSerializer(osd).data)


class UserViewSet(viewsets.ModelViewSet):
    """
    The Calamari UI/API user account information
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserMe(APIView):
    """
Return information about the current user. If the user is not authenticated
(i.e. an anonymous user), then 401 is returned with an error message.
    """
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    @never_cache
    def get(self, request):
        if request.user.is_authenticated():
            return Response(self.serializer_class(request.user).data)
        return Response({
            'message': 'Session expired or invalid',
        }, status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
@ensure_csrf_cookie
@never_cache
def login(request):
    """
This resource is used to authenticate with the REST API by POSTing a message
as follows:

::

    {
        "username": "<username>",
        "password": "<password>"
    }

If authentication is successful, 200 is returned, if it is unsuccessful
then 401 is returend.
    """
    if request.method == 'POST':
        username = request.DATA.get('username', None)
        password = request.DATA.get('password', None)
        msg = {}
        if not username:
            msg['username'] = 'This field is required'
        if not password:
            msg['password'] = 'This field is required'
        if len(msg) > 0:
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if not user:
            return Response({
                'message': 'User authentication failed'
            }, status=status.HTTP_401_UNAUTHORIZED)
        auth_login(request, user)
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
        return Response({})
    else:
        pass
    request.session.set_test_cookie()
    return Response({})


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
def logout(request):
    """
The resource is used to terminate an authenticated session by POSTing an
empty request.
    """
    auth_logout(request)
    return Response({'message': 'Logged out'})


def _get_local_grains():
    """
    Return the salt grains for this host that we are running
    on.  If we support SELinux in the future this may need
    to be moved into a cthulhu RPC as the apache worker may
    not have the right capabilities to query all the grains.
    """
    # Stash grains as an attribute of this function
    if not hasattr(_get_local_grains, 'grains'):
        # Use salt to get an interesting subset of the salt grains (getting
        # everything is a bit slow)
        grains = {}
        c = master_config(config.get('cthulhu', 'salt_config_path'))
        l = _create_loader(c, 'grains', 'grain')
        funcs = l.gen_functions()
        for key in [k for k in funcs.keys() if k.startswith('core.')]:
            ret = funcs[key]()
            if isinstance(ret, dict):
                grains.update(ret)
        _get_local_grains.grains = grains
    else:
        grains = _get_local_grains.grains

    return grains


class Info(APIView):
    """
Provides metadata about the installation of Calamari server in use
    """
    permission_classes = (AllowAny,)
    serializer_class = InfoSerializer

    def get(self, request):
        grains = _get_local_grains()

        try:
            ipaddr = socket.gethostbyname(grains['fqdn'])
        except socket.gaierror:
            # It is annoying, but not rare, to have a host
            # that cannot resolve its own name.
            # From a dict of interface name to list of addresses,
            # we pick the first address from the first interface
            # which has some addresses and isn't a loopback.
            ipaddr = [addrs for name, addrs in grains['ip_interfaces'].items() if
                      name not in ['lo', 'lo0'] and addrs][0][0]

        proto = "https" if request.is_secure() else "http"
        bootstrap_url = "{0}://{1}{2}".format(proto, request.META['HTTP_HOST'], reverse('bootstrap'))
        BOOTSTRAP_UBUNTU = "wget -O - {url} | sudo python"
        BOOTSTRAP_RHEL = "curl {url} | python"

        return Response(self.serializer_class(DataObject({
            "version": "2.0",  # TODO: populate from build version (ticket #7082)
            "license": "N/A",
            "registered": "N/A",
            "hostname": grains['host'],
            "fqdn": grains['fqdn'],
            "ipaddr": ipaddr,
            "bootstrap_url": bootstrap_url,
            "bootstrap_ubuntu": BOOTSTRAP_UBUNTU.format(url=bootstrap_url),
            "bootstrap_rhel": BOOTSTRAP_RHEL.format(url=bootstrap_url),
        })).data)


class ClusterViewSet(RPCViewSet):
    serializer_class = ClusterSerializer

    def list(self, request):
        clusters = [DataObject(c) for c in self.client.list_clusters()]

        return Response(ClusterSerializer(clusters, many=True).data)

    def retrieve(self, request, pk):
        cluster_data = self.client.get_cluster(pk)
        if not cluster_data:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            cluster = DataObject(cluster_data)
            return Response(ClusterSerializer(cluster).data)


class ServerViewSet(RPCViewSet):
    serializer_class = ServerSerializer

    def retrieve(self, request, pk):
        return Response(
            self.serializer_class(DataObject(self.client.server_get(pk))).data
        )

    def list(self, request, fsid):
        return Response(
            self.serializer_class([DataObject(s) for s in self.client.server_list_cluster(fsid)], many=True).data)


class PoolViewSet(RPCViewSet):
    serializer_class = PoolSerializer

    def pool_object(self, pool_data, cluster):
        return DataObject({
            'id': pool_data['pool'],
            'cluster': cluster['id'],
            'pool_id': pool_data['pool'],
            'name': pool_data['pool_name'],
            'quota_max_objects': pool_data['quota_max_objects'],
            'quota_max_bytes': pool_data['quota_max_bytes'],
            # TODO: change names to FSIDs for #6883
            'used_objects': get_latest_graphite("ceph.cluster.%s.pool.%s.num_objects" % (cluster['name'], pool_data['pool'])),
            'used_bytes': get_latest_graphite("ceph.cluster.%s.pool.%s.num_bytes" % (cluster['name'], pool_data['pool']))
        })

    def list(self, request, fsid):
        cluster = self.client.get_cluster(fsid)
        pools = [self.pool_object(p, cluster) for p in self.client.list(fsid, POOL)]

        return Response(PoolSerializer(pools, many=True).data)

    def retrieve(self, request, fsid, pool_id):
        cluster = self.client.get_cluster(fsid)
        pool = self.pool_object(self.client.get(fsid, POOL, int(pool_id)), cluster)
        return Response(PoolSerializer(pool).data)
