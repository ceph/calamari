from collections import defaultdict
import logging
import socket

from django.core.exceptions import ValidationError, PermissionDenied
from django.core.urlresolvers import reverse
from django.http import Http404
import pytz
from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed
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

# Suppress warning from graphite's use of old django API
import warnings
import zerorpc

warnings.filterwarnings("ignore", category=DeprecationWarning,
                        message="django.conf.urls.defaults is deprecated")

try:
    import graphite
except ImportError:
    graphite = None
else:
    from graphite.render.attime import parseATTime
    from graphite.render.datalib import fetchData

from calamari_rest.views.rpc_view import DataObject, RPCViewSet
from calamari_rest.viewsets import RoleLimitedViewSet
from calamari_common.types import POOL, OSD, ServiceId, OsdMap, PgSummary, MdsMap, MonStatus
from calamari_rest.views.server_metadata import get_local_grains

try:
    from calamari_rest.version import VERSION
except ImportError:
    # could create version here if we wanted to be fancier
    VERSION = 'dev'


from calamari_rest.serializers.v1 import ClusterSpaceSerializer, ClusterHealthSerializer, UserSerializer, \
    ClusterSerializer, OSDDetailSerializer, OSDListSerializer, ClusterHealthCountersSerializer, \
    PoolSerializer, ServerSerializer, InfoSerializer
from calamari_common.config import CalamariConfig


config = CalamariConfig()

log = logging.getLogger('django.request')


def _get_latest_graphite(metric):
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


def get_latest_graphite(metric):
    """
    Wrapper to hide the case where graphite is unavailable
    """
    if graphite is not None:
        return _get_latest_graphite(metric)
    else:
        # In the absence of graphite, talk to a ShallowCarbonCache instance
        client = zerorpc.Client()
        try:
            client.connect("tcp://127.0.0.1:5051")

            return client.get_latest([metric])[metric]
        finally:
            client.close()


class Space(RPCViewSet):
    serializer_class = ClusterSpaceSerializer

    def get(self, request, fsid):
        def to_bytes(kb):
            if kb is not None:
                return kb * 1024
            else:
                return None

        df_path = lambda stat_name: "ceph.cluster.{0}.df.{1}".format(fsid, stat_name)
        # Check for old vs. new stats (changed in Ceph Firefly)
        # see Ceph commit ee2dbdb0f5e54fe6f9c5999c032063b084424c4c
        # Old:          New:
        # total_used    total_used_bytes
        # total_space   total_bytes
        # total_avail   total_avail_bytes
        #
        # the old stats are in terms of kB (must multiply to get bytes);
        # the new ones are already in bytes.  Check new versions first
        # so that old relics in the database after upgrade stop being
        # used.
        if get_latest_graphite(df_path('total_used_bytes')) is not None:
            space = {
                'used_bytes': get_latest_graphite(df_path('total_used_bytes')),
                'capacity_bytes': get_latest_graphite(df_path('total_bytes')),
                'free_bytes': get_latest_graphite(df_path('total_avail_bytes'))
            }
        else:
            space = {
                'used_bytes': to_bytes(get_latest_graphite(df_path('total_used'))),
                'capacity_bytes': to_bytes(get_latest_graphite(df_path('total_space'))),
                'free_bytes': to_bytes(get_latest_graphite(df_path('total_avail')))
            }

        return Response(ClusterSpaceSerializer(DataObject({
            'space': space
        })).data)


class Health(RPCViewSet):
    serializer_class = ClusterHealthSerializer

    def get(self, request, fsid):
        health = self.client.get_sync_object(fsid, 'health')
        return Response(ClusterHealthSerializer(DataObject({
            'report': health,
            'cluster_update_time': self.client.get_cluster(fsid)['update_time'],
            'cluster_update_time_unix': self.client.get_cluster(fsid)['update_time'],
        })).data)


class HealthCounters(RPCViewSet):
    serializer_class = ClusterHealthCountersSerializer

    PG_FIELDS = ['pgid', 'acting', 'up', 'state']

    CRIT_STATES = set(['stale', 'down', 'peering', 'inconsistent', 'incomplete', 'inactive'])
    WARN_STATES = set(['creating', 'recovery_wait', 'recovering', 'replay',
                       'splitting', 'degraded', 'remapped', 'scrubbing', 'repair',
                       'wait_backfill', 'backfilling', 'backfill_toofull'])
    OKAY_STATES = set(['active', 'clean'])

    @classmethod
    def generate(cls, osd_map, mds_map, mon_status, pg_summary):
        return {
            'osd': cls._calculate_osd_counters(osd_map),
            'mds': cls._calculate_mds_counters(mds_map),
            'mon': cls._calculate_mon_counters(mon_status),
            'pg': cls._calculate_pg_counters(pg_summary),
        }

    @classmethod
    def _calculate_mon_counters(cls, mon_status):
        mons = mon_status['monmap']['mons']
        quorum = mon_status['quorum']
        ok, warn, crit = 0, 0, 0
        for mon in mons:
            rank = mon['rank']
            if rank in quorum:
                ok += 1
            # TODO: use 'have we had a salt heartbeat recently' here instead
            # elif self.try_mon_connect(mon):
            #    warn += 1
            else:
                crit += 1
        return {
            'ok': {
                'count': ok,
                'states': {} if ok == 0 else {'in': ok},
            },
            'warn': {
                'count': warn,
                'states': {} if warn == 0 else {'up': warn},
            },
            'critical': {
                'count': crit,
                'states': {} if crit == 0 else {'out': crit},
            }
        }

    @classmethod
    def _pg_counter_helper(cls, states, classifier, count, stats):
        matched_states = classifier.intersection(states)
        if len(matched_states) > 0:
            stats[0] += count
            for state in matched_states:
                stats[1][state] += count
            return True
        return False

    @classmethod
    def _calculate_pg_counters(cls, pg_summary):
        # Although the mon already has a copy of this (in 'status' output),
        # it's such a simple thing to recalculate here and simplifies our
        # sync protocol.

        all_states = cls.CRIT_STATES | cls.WARN_STATES | cls.OKAY_STATES

        pgs_by_state = pg_summary['all']
        ok, warn, crit = [[0, defaultdict(int)] for _ in range(3)]
        for state_name, count in pgs_by_state.items():
            states = map(lambda s: s.lower(), state_name.split("+"))
            if cls._pg_counter_helper(states, cls.CRIT_STATES, count, crit):
                pass
            elif cls._pg_counter_helper(states, cls.WARN_STATES, count, warn):
                pass
            elif cls._pg_counter_helper(states, cls.OKAY_STATES, count, ok):
                pass
            else:
                # Uncategorised state, assume it's critical.  This shouldn't usually
                # happen, but want to avoid breaking if ceph adds a state.
                crit[0] += count
                for state in states:
                    if state not in all_states or state in cls.CRIT_STATES:
                        crit[1][state] += count

        return {
            'ok': {
                'count': ok[0],
                'states': dict(ok[1]),
            },
            'warn': {
                'count': warn[0],
                'states': dict(warn[1]),
            },
            'critical': {
                'count': crit[0],
                'states': dict(crit[1]),
            },
        }

    @classmethod
    def _calculate_osd_counters(cls, osd_map):
        osds = osd_map['osds']
        counters = {
            'total': len(osds),
            'not_up_not_in': 0,
            'not_up_in': 0,
            'up_not_in': 0,
            'up_in': 0
        }
        for osd in osds:
            up, inn = osd['up'], osd['in']
            if not up and not inn:
                counters['not_up_not_in'] += 1
            elif not up and inn:
                counters['not_up_in'] += 1
            elif up and not inn:
                counters['up_not_in'] += 1
            elif up and inn:
                counters['up_in'] += 1
        warn_count = counters['up_not_in'] + counters['not_up_in']
        warn_states = {}
        if counters['up_not_in'] > 0:
            warn_states['up/out'] = counters['up_not_in']
        if counters['not_up_in'] > 0:
            warn_states['down/in'] = counters['not_up_in']
        return {
            'ok': {
                'count': counters['up_in'],
                'states': {} if counters['up_in'] == 0 else {'up/in': counters['up_in']},
            },
            'warn': {
                'count': warn_count,
                'states': {} if warn_count == 0 else warn_states,
            },
            'critical': {
                'count': counters['not_up_not_in'],
                'states': {} if counters['not_up_not_in'] == 0 else {'down/out': counters['not_up_not_in']},
            },
        }

    @classmethod
    def _calculate_mds_counters(cls, mds_map):
        up = len(mds_map['up'])
        inn = len(mds_map['in'])
        total = len(mds_map['info'])
        return {
            'total': total,
            'up_in': inn,
            'up_not_in': up - inn,
            'not_up_not_in': total - up,
        }

    def get(self, request, fsid):
        osd_data = self.client.get_sync_object(fsid, OsdMap.str, async=True)
        mds_data = self.client.get_sync_object(fsid, MdsMap.str, async=True)
        pg_summary = self.client.get_sync_object(fsid, PgSummary.str, async=True)
        mon_status = self.client.get_sync_object(fsid, MonStatus.str, async=True)
        mds_data = mds_data.get()
        osd_data = osd_data.get()
        pg_summary = pg_summary.get()
        mon_status = mon_status.get()

        counters = self.generate(osd_data, mds_data, mon_status, pg_summary)

        return Response(ClusterHealthCountersSerializer(DataObject({
            'counters': counters,
            'cluster_update_time': self.client.get_cluster(fsid)['update_time']
        })).data)


class OSDList(RPCViewSet):
    """
    Provides an object which includes a list of all OSDs, and
    some summary counters (pg_state_counts)
    """
    serializer_class = OSDListSerializer

    OSD_FIELDS = ['uuid', 'up', 'in', 'up_from', 'public_addr',
                  'cluster_addr', 'heartbeat_back_addr', 'heartbeat_front_addr']

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

    def generate(self, pg_summary, osd_map, service_to_server, servers):
        fqdn_to_server = dict([(s['fqdn'], s) for s in servers])

        # map osd id to pg states
        pg_states_by_osd = defaultdict(lambda: defaultdict(lambda: 0))
        # map osd id to set of pools
        pools_by_osd = defaultdict(lambda: set([]))
        # map pg state to osd ids
        osds_by_pg_state = defaultdict(lambda: set([]))

        # get the list of pools
        pools_by_id = dict((p_id, p['pool_name']) for (p_id, p) in osd_map.pools_by_id.items())

        for pool_id, osds in osd_map.osds_by_pool.items():
            for osd_id in osds:
                pools_by_osd[osd_id].add(pools_by_id[pool_id])

        for osd_id, osd_pg_summary in pg_summary['by_osd'].items():
            for state_tuple, count in osd_pg_summary.items():
                for state in state_tuple.split("+"):
                    osds_by_pg_state[state].add(osd_id)
                    pg_states_by_osd[osd_id][state] += count

        # convert set() to list to make JSON happy
        osds_by_pg_state = dict((k, list(v)) for k, v in
                                osds_by_pg_state.iteritems())

        # Merge the PgSummary data into the OsdMap data
        def fixup_osd(osd):
            osd_id = osd['osd']
            data = dict((k, osd[k]) for k in self.OSD_FIELDS)
            data.update({'id': osd_id})
            data.update({'osd': osd_id})
            data.update({'pg_states': dict(pg_states_by_osd[osd_id])})
            data.update({'pools': list(pools_by_osd[osd_id])})

            return data

        osds = map(fixup_osd, osd_map.osds_by_id.values())

        # Apply the ServerMonitor data
        for o, (service_id, fqdn) in zip(osds, service_to_server):
            o['fqdn'] = fqdn
            if fqdn is not None:
                o['host'] = fqdn_to_server[fqdn]['hostname']
            else:
                o['host'] = None

        return osds, osds_by_pg_state

    def get(self, request, fsid):
        servers = self.client.server_list_cluster(fsid, async=True)
        osd_data = self.client.get_sync_object(fsid, OsdMap.str, async=True)
        osds = self.client.list(fsid, OSD, {}, async=True)
        pg_summary = self.client.get_sync_object(fsid, PgSummary.str, async=True)
        osds = osds.get()
        servers = servers.get()
        osd_data = osd_data.get()
        pg_summary = pg_summary.get()

        osd_map = OsdMap(None, osd_data)

        server_info = self.client.server_by_service([ServiceId(fsid, OSD, str(osd['osd'])) for osd in osds], async=True)
        server_info = server_info.get()

        osds, osds_by_pg_state = self.generate(pg_summary, osd_map, server_info, servers)

        if not osds or not osds_by_pg_state:
            return Response([], status.HTTP_202_ACCEPTED)

        pg_states = request.QUERY_PARAMS.get('pg_states', None)
        if pg_states:
            osds = self._filter_by_pg_state(osds, pg_states, osds_by_pg_state)

        osd_list = DataObject({
            # 'osds': [DataObject({'osd': o}) for o in osds],
            'osds': osds,
            'osds_by_pg_state': osds_by_pg_state
        })

        return Response(OSDListSerializer(osd_list).data)


class OSDDetail(RPCViewSet):
    """
    This is the same data that is provided in the OSD list, but for
    a single OSD, and not including the pg_state_counts.
    """
    serializer_class = OSDDetailSerializer

    def get(self, request, fsid, osd_id):
        data = self.client.get(fsid, 'osd', int(osd_id))
        osd = DataObject({'osd': data})
        return Response(OSDDetailSerializer(osd).data)


class UserViewSet(viewsets.ModelViewSet, RoleLimitedViewSet):
    """
    The Calamari UI/API user account information.

    You may pass 'me' as the user ID to refer to the currently logged in user,
    otherwise the user ID is a numeric ID.

    Users can only modify their own account (i.e.
    the user being modified must be the user associated with the current login session).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def _get_user(self, request, user_id):
        if user_id == "me":
            if request.user.is_authenticated():
                return request.user
            else:
                raise AuthenticationFailed()
        else:
            try:
                user = self.queryset.get(pk=user_id)
            except User.DoesNotExist:
                raise Http404("User not found")
            else:
                return user

    def update(self, request, *args, **kwargs):
        # Note that unlike the parent update() we do not support
        # creating users with PUT.
        partial = kwargs.pop('partial', False)
        user = self.get_object()

        if user.id != self.request.user.id:
            raise PermissionDenied("May not change another user's password")

        serializer = self.get_serializer(user, data=request.DATA, partial=partial)

        if serializer.is_valid():
            try:
                self.pre_save(serializer.object)
            except ValidationError as err:
                # full_clean on model instance may be called in pre_save, so we
                # have to handle eventual errors.
                return Response(err.message_dict, status=status.HTTP_400_BAD_REQUEST)
            user = serializer.save(force_update=True)
            log.debug("saved user %s" % user)
            # self.post_save(user, created=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, queryset=None):
        user = self._get_user(self.request, self.kwargs['pk'])
        if self.kwargs['pk'] == 'me':
            self.kwargs['pk'] = user.id
        return user


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


class Info(APIView):
    """
Provides metadata about the installation of Calamari server in use
    """
    permission_classes = (AllowAny,)
    serializer_class = InfoSerializer

    def get(self, request):
        grains = get_local_grains()

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
        BOOTSTRAP_RHEL = "curl {url} | sudo python"

        return Response(self.serializer_class(DataObject({
            "version": str(VERSION),
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
            'used_objects': get_latest_graphite("ceph.cluster.%s.pool.%s.num_objects" % (cluster['id'], pool_data['pool'])),
            'used_bytes': get_latest_graphite("ceph.cluster.%s.pool.%s.num_bytes" % (cluster['id'], pool_data['pool']))
        })

    def list(self, request, fsid):
        cluster = self.client.get_cluster(fsid)
        pools = [self.pool_object(p, cluster) for p in self.client.list(fsid, POOL, {})]

        return Response(PoolSerializer(pools, many=True).data)

    def retrieve(self, request, fsid, pool_id):
        cluster = self.client.get_cluster(fsid)
        pool = self.pool_object(self.client.get(fsid, POOL, int(pool_id)), cluster)
        return Response(PoolSerializer(pool).data)
