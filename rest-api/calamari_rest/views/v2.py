from collections import defaultdict
import logging

from dateutil.parser import parse as dateutil_parse
from django.http import Http404
from rest_framework.exceptions import ParseError, APIException
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib.auth.decorators import login_required

from calamari_rest.serializers.v2 import PoolSerializer, CrushRuleSetSerializer, CrushRuleSerializer, \
    ServerSerializer, SimpleServerSerializer, SaltKeySerializer, RequestSerializer, \
    ClusterSerializer, EventSerializer, LogTailSerializer, OsdSerializer, ConfigSettingSerializer, MonSerializer, OsdConfigSerializer
from calamari_rest.views.database_view_set import DatabaseViewSet
from calamari_rest.views.paginated_mixin import PaginatedMixin
from calamari_rest.views.rpc_view import RPCViewSet, DataObject
from calamari_rest.views.v1 import _get_local_grains
from calamari_common.config import CalamariConfig
from calamari_common.types import CRUSH_RULE, POOL, OSD, USER_REQUEST_COMPLETE, USER_REQUEST_SUBMITTED, \
    OSD_IMPLEMENTED_COMMANDS, MON, OSD_MAP, SYNC_OBJECT_TYPES, ServiceId, NotFound
from calamari_common.db.event import Event, severity_from_str, SEVERITIES
import salt.client

from django.views.decorators.csrf import csrf_exempt
config = CalamariConfig()

log = logging.getLogger('django.request')


if log.level <= logging.DEBUG:
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    for handler in log.handlers:
        logging.getLogger('sqlalchemy.engine').addHandler(handler)


@api_view(['GET'])
@login_required
def grains(request):
    """
The salt grains for the host running Calamari server.  These are variables
from Saltstack that tell us useful properties of the host.

The fields in this resource are passed through verbatim from SaltStack, see
the examples for which fields are available.
    """
    return Response(_get_local_grains())


class RequestViewSet(RPCViewSet, PaginatedMixin):
    """
Calamari server requests, tracking long-running operations on the Calamari server.  Some
API resources return a ``202 ACCEPTED`` response with a request ID, which you can use with
this resource to learn about progress and completion of an operation.  This resource is
paginated.

May optionally filter by state by passing a ``?state=<state>`` GET parameter, where
state is one of 'complete', 'submitted'.

The returned records are ordered by the 'requested_at' attribute, in descending order (i.e.
the first page of results contains the most recent requests).
    """
    serializer_class = RequestSerializer

    def retrieve(self, request, fsid, request_id):
        user_request = DataObject(self.client.get_request(fsid, request_id))
        return Response(RequestSerializer(user_request).data)

    def list(self, request, fsid):
        filter_state = request.GET.get('state', None)
        valid_states = [USER_REQUEST_COMPLETE, USER_REQUEST_SUBMITTED]
        if filter_state is not None and filter_state not in valid_states:
            raise ParseError("State must be one of %s" % ", ".join(valid_states))

        requests = self.client.list_requests(fsid, filter_state)
        return Response(self._paginate(request, requests))


class CrushRuleViewSet(RPCViewSet):
    """
A CRUSH ruleset is a collection of CRUSH rules which are applied
together to a pool.
    """
    serializer_class = CrushRuleSerializer

    def list(self, request, fsid):
        rules = self.client.list(fsid, CRUSH_RULE)
        osds_by_rule_id = self.client.get_sync_object(fsid, 'osd_map', ['osds_by_rule_id'])
        for rule in rules:
            rule['osd_count'] = len(osds_by_rule_id[rule['rule_id']])
        return Response(CrushRuleSerializer([DataObject(r) for r in rules], many=True).data)


class CrushRuleSetViewSet(RPCViewSet):
    """
A CRUSH rule is used by Ceph to decide where to locate placement groups on OSDs.
    """
    serializer_class = CrushRuleSetSerializer

    def list(self, request, fsid):
        rules = self.client.list(fsid, CRUSH_RULE)
        osds_by_rule_id = self.client.get_sync_object(fsid, 'osd_map', ['osds_by_rule_id'])
        rulesets_data = defaultdict(list)
        for rule in rules:
            rule['osd_count'] = len(osds_by_rule_id[rule['rule_id']])
            rulesets_data[rule['ruleset']].append(rule)

        rulesets = [DataObject({
            'id': rd_id,
            'rules': [DataObject(r) for r in rd_rules]
        }) for (rd_id, rd_rules) in rulesets_data.items()]

        return Response(CrushRuleSetSerializer(rulesets, many=True).data)


class SaltKeyViewSet(RPCViewSet):
    """
Ceph servers authentication with the Calamari using a key pair.  Before
Calamari accepts messages from a server, the server's key must be accepted.
    """
    serializer_class = SaltKeySerializer

    def list(self, request):
        return Response(self.serializer_class(self.client.minion_status(None), many=True).data)

    def partial_update(self, request, minion_id):
        self._partial_update(minion_id, request.DATA)

        # TODO handle 404

        return Response(status=status.HTTP_204_NO_CONTENT)

    def _partial_update(self, minion_id, data):
        valid_status = ['accepted', 'rejected']
        if not 'status' in data:
            raise ParseError({'status': "This field is mandatory"})
        elif data['status'] not in valid_status:
            raise ParseError({'status': "Must be one of %s" % ",".join(valid_status)})
        else:
            # TODO validate transitions, cannot go from rejected to accepted.
            if data['status'] == 'accepted':
                self.client.minion_accept(minion_id)
            elif data['status'] == 'rejected':
                self.client.minion_reject(minion_id)
            else:
                raise NotImplementedError()

    def _validate_list(self, request):
        keys = request.DATA
        if not isinstance(keys, list):
            return Response("Bulk PATCH must send a list", status=status.HTTP_400_BAD_REQUEST)
        for key in keys:
            if not 'id' in key:
                return Response("Items in bulk PATCH must have 'id' attribute", status=status.HTTP_400_BAD_REQUEST)

    def list_partial_update(self, request):
        self._validate_list(request)

        keys = request.DATA
        log.debug("KEYS %s" % keys)
        for key in keys:
            self._partial_update(key['id'], key)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, minion_id):
        # TODO handle 404
        self.client.minion_delete(minion_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list_destroy(self, request):
        self._validate_list(request)
        keys = request.DATA
        for key in keys:
            self.client.minion_delete(key['id'])

        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, minion_id):
        return Response(self.serializer_class(self.client.minion_get(minion_id)).data)


class ClusterViewSet(RPCViewSet):
    """
A Ceph cluster, uniquely identified by its FSID.  All Ceph services such
as OSDs and mons are namespaced within a cluster.  Servers may host services
for more than one cluster, although usually they only hold one.

Note that the ``name`` attribute of a Ceph cluster has no uniqueness,
code consuming this API should always use the FSID to identify clusters.

Using the DELETE verb on a Ceph cluster will cause the Calamari server
to drop its records of the cluster and services within the cluster.  However,
if the cluster still exists on servers managed by Calamari, it will be immediately
redetected: only use DELETE on clusters which really no longer exist.
    """
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

    def destroy(self, request, pk):
        self.client.delete_cluster(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PoolDataObject(DataObject):
    """
    Slightly dressed up version of the raw pool from osd dump
    """

    FLAG_HASHPSPOOL = 1
    FLAG_FULL = 2

    @property
    def hashpspool(self):
        return bool(self.flags & self.FLAG_HASHPSPOOL)

    @property
    def full(self):
        return bool(self.flags & self.FLAG_FULL)


class RequestReturner(object):
    """
    Helper for ViewSets that sometimes need to return a request handle
    """
    def _return_request(self, request):
        if request:
            return Response(request, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_304_NOT_MODIFIED)


class NullableDataObject(DataObject):
    """
    A DataObject which synthesizes Nones for any attributes it doesn't have
    """
    def __getattr__(self, item):
        if not item.startswith('_'):
            return self.__dict__.get(item, None)
        else:
            raise AttributeError


class ServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Service unavailable"


class ConfigViewSet(RPCViewSet):
    """
Configuration settings from a Ceph Cluster.
    """
    serializer_class = ConfigSettingSerializer

    def _get_config(self, fsid):
        ceph_config = self.client.get_sync_object(fsid, 'config')
        if not ceph_config:
            raise ServiceUnavailable("Cluster configuration unavailable")
        else:
            return ceph_config

    def list(self, request, fsid):
        ceph_config = self._get_config(fsid)
        settings = [DataObject({'key': k, 'value': v}) for (k, v) in ceph_config.items()]
        return Response(self.serializer_class(settings, many=True).data)

    def retrieve(self, request, fsid, key):
        ceph_config = self._get_config(fsid)
        try:
            setting = DataObject({'key': key, 'value': ceph_config[key]})
        except KeyError:
            raise Http404("Key '%s' not found" % key)
        else:
            return Response(self.serializer_class(setting).data)


def _config_to_bool(config_val):
    return {'true': True, 'false': False}[config_val.lower()]


class PoolViewSet(RPCViewSet, RequestReturner):
    """
Manage Ceph storage pools.

To get the default values which will be used for any fields omitted from a POST, do
a GET with the ?defaults argument.  The returned pool object will contain all attributes,
but those without static defaults will be set to null.

    """
    serializer_class = PoolSerializer

    def _defaults(self, fsid):

        ceph_config = self.client.get_sync_object(fsid, 'config')
        if not ceph_config:
            return Response("Cluster configuration unavailable", status=status.HTTP_503_SERVICE_UNAVAILABLE)

        defaults = NullableDataObject({
            'size': int(ceph_config['osd_pool_default_size']),
            'crush_ruleset': int(ceph_config['osd_pool_default_crush_rule']),
            'min_size': int(ceph_config['osd_pool_default_min_size']),
            'hashpspool': _config_to_bool(ceph_config['osd_pool_default_flag_hashpspool']),
            # Crash replay interval is zero by default when you create a pool, but when ceph creates
            # its own data pool it applies 'osd_default_data_pool_replay_window'.  If we add UI for adding
            # pools to a filesystem, we should check that those data pools have this set.
            'crash_replay_interval': 0,
            'quota_max_objects': 0,
            'quota_max_bytes': 0
        })

        return Response(PoolSerializer(defaults).data)

    def list(self, request, fsid):
        if 'defaults' in request.GET:
            return self._defaults(fsid)

        pools = [PoolDataObject(p) for p in self.client.list(fsid, POOL)]
        return Response(PoolSerializer(pools, many=True).data)

    def retrieve(self, request, fsid, pool_id):
        pool = PoolDataObject(self.client.get(fsid, POOL, int(pool_id)))
        return Response(PoolSerializer(pool).data)

    def create(self, request, fsid):
        serializer = PoolSerializer(data=request.DATA)
        if serializer.is_valid():
            create_response = self.client.create(fsid, POOL, request.DATA)
            # TODO: handle case where the creation is rejected for some reason (should
            # be passed an errors dict for a clean failure, or a zerorpc exception
            # for a dirty failure)
            assert 'request_id' in create_response
            return Response(create_response, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, fsid, pool_id):
        delete_response = self.client.delete(fsid, POOL, int(pool_id), status=status.HTTP_202_ACCEPTED)
        return Response(delete_response, status=status.HTTP_202_ACCEPTED)

    def update(self, request, fsid, pool_id):
        updates = request.DATA
        # TODO: validation, but we don't want to check all fields are present (because
        # this is a PATCH), just that those present are valid.  rest_framework serializer
        # may or may not be able to do that out the box.
        return self._return_request(self.client.update(fsid, POOL, int(pool_id), updates))


class OsdViewSet(RPCViewSet, RequestReturner):
    """
Manage Ceph OSDs.

Apply ceph commands to an OSD by doing a POST with no data to
api/v2/cluster/<fsid>/osd/<osd_id>/command/<command>
where <command> is one of ("scrub", "deep-scrub", "repair")

e.g. Initiate a scrub on OSD 0 by POSTing {} to api/v2/cluster/<fsid>/osd/0/command/scrub

Pass a ``pool`` URL parameter set to a pool ID to filter by pool.

    """
    serializer_class = OsdSerializer

    def list(self, request, fsid):
        osds = self.client.get_sync_object(fsid, 'osd_map', ['osds_by_id']).values()

        if 'pool' in request.GET:
            try:
                pool_id = int(request.GET['pool'])
            except ValueError:
                return Response("Pool ID must be an integer", status=status.HTTP_400_BAD_REQUEST)
            osds_in_pool = self.client.get_sync_object(fsid, 'osd_map', ['osds_by_pool', pool_id])
            if osds_in_pool is None:
                return Response("Unknown pool ID", status=status.HTTP_400_BAD_REQUEST)

            osds = [o for o in osds if o['osd'] in osds_in_pool]

        crush_nodes = self.client.get_sync_object(fsid, 'osd_map', ['osd_tree_node_by_id'])
        for o in osds:
            o.update({'reweight': crush_nodes[o['osd']]['reweight']})

        server_info = self.client.server_by_service([ServiceId(fsid, OSD, str(osd['osd'])) for osd in osds])
        for o, (service_id, fqdn) in zip(osds, server_info):
            o['server'] = fqdn

        osd_to_pools = self.client.get_sync_object(fsid, 'osd_map', ['osd_pools'])
        for o in osds:
            o['pools'] = osd_to_pools[o['osd']]

        osd_commands = self.client.get_valid_commands(fsid, OSD, [x['osd'] for x in osds])
        for o in osds:
            o.update(osd_commands[o['osd']])

        return Response(self.serializer_class([DataObject(o) for o in osds], many=True).data)

    @csrf_exempt
    def retrieve(self, request, fsid, osd_id):
        osd = self.client.get_sync_object(fsid, 'osd_map', ['osds_by_id', int(osd_id)])
        crush_node = self.client.get_sync_object(fsid, 'osd_map', ['osd_tree_node_by_id', int(osd_id)])
        osd['reweight'] = crush_node['reweight']
        osd['server'] = self.client.server_by_service([ServiceId(fsid, OSD, osd_id)])[0][1]

        pools = self.client.get_sync_object(fsid, 'osd_map', ['osd_pools', int(osd_id)])
        osd['pools'] = pools

        osd_commands = self.client.get_valid_commands(fsid, OSD, [int(osd_id)])
        osd.update(osd_commands[int(osd_id)])

        return Response(self.serializer_class(DataObject(osd)).data)

    def update(self, request, fsid, osd_id):
        return self._return_request(self.client.update(fsid, OSD, int(osd_id), dict(request.DATA)))

    def apply(self, request, fsid, osd_id, command):
        if command in self.client.get_valid_commands(fsid, OSD, [int(osd_id)]).get(int(osd_id)).get('valid_commands'):
            return Response(self.client.apply(fsid, OSD, int(osd_id), command), status=202)
        else:
            return Response('{0} not valid on {1}'.format(command, osd_id), status=403)

    def get_implemented_commands(self, request, fsid):
        return Response(OSD_IMPLEMENTED_COMMANDS)

    def get_valid_commands(self, request, fsid, osd_id=None):
        osds = []
        if osd_id is None:
            osds = self.client.get_sync_object(fsid, 'osd_map', ['osds_by_id']).keys()
        else:
            osds.append(int(osd_id))

        return Response(self.client.get_valid_commands(fsid, OSD, osds))

    def validate_command(self, request, fsid, osd_id, command):
        valid_commands = self.client.get_valid_commands(fsid, OSD, [int(osd_id)]).get(int(osd_id)).get('valid_commands')

        return Response({'valid': command in valid_commands})


class OsdConfigViewSet(RPCViewSet, RequestReturner):
    """
Manage flags in the OsdMap
    """
    serializer_class = OsdConfigSerializer

    def osd_config(self, request, fsid):
        osd_map = self.client.get_sync_object(fsid, OSD_MAP, ['flags'])
        return Response(osd_map)

    def update(self, request, fsid):
        return self._return_request(self.client.update(fsid, OSD_MAP, None, dict(request.DATA)))


class SyncObject(RPCViewSet):
    """
These objects are the raw data received by the Calamari server from the Ceph cluster,
such as the cluster maps
    """

    def retrieve(self, request, fsid, sync_type):
        return Response(self.client.get_sync_object(fsid, sync_type))

    def describe(self, request, fsid):
        return Response([s.str for s in SYNC_OBJECT_TYPES])


class ServerClusterViewSet(RPCViewSet):
    """
View of servers within a particular cluster.

Use the global server view for DELETE operations (there is no
concept of deleting a server from a cluster, only deleting
all record of it from any/all clusters).
    """
    serializer_class = ServerSerializer

    def metadata(self, request):
        m = super(ServerClusterViewSet, self).metadata(request)
        m['name'] = "Server (within cluster)"
        return m

    def list(self, request, fsid):
        return Response(self.serializer_class(
            [DataObject(s) for s in self.client.server_list_cluster(fsid)], many=True).data)

    def retrieve(self, request, fsid, fqdn):
        return Response(self.serializer_class(DataObject(self.client.server_get_cluster(fqdn, fsid))).data)


class ServerViewSet(RPCViewSet):
    """
Servers which are in communication with Calamari server, or which
have been inferred from the OSD map.  If a server is in communication
with the Calamari server then it is considered *managed*.

If a server is only known via the OSD map, then the FQDN attribute
will be set to the hostname.  This server is later added as a managed
server then the FQDN will be modified to its correct value.
    """
    serializer_class = SimpleServerSerializer

    def retrieve_grains(self, request, fqdn):
        import salt.config
        import salt.utils.master

        salt_config = salt.config.client_config(config.get('cthulhu', 'salt_config_path'))
        pillar_util = salt.utils.master.MasterPillarUtil(fqdn, 'glob',
                                                         use_cached_grains=True,
                                                         grains_fallback=False,
                                                         opts=salt_config)
        try:
            return Response(pillar_util.get_minion_grains()[fqdn])
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, fqdn):
        return Response(
            self.serializer_class(DataObject(self.client.server_get(fqdn))).data
        )

    def list(self, request):
        return Response(self.serializer_class([DataObject(s) for s in self.client.server_list()], many=True).data)

    def destroy(self, request, fqdn):
        self.client.server_delete(fqdn)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EventViewSet(DatabaseViewSet, PaginatedMixin):
    """
Events generated by Calamari server in response to messages from
servers and Ceph clusters.  This resource is paginated.

Note that events are not visible synchronously with respect to
all other API resources.  For example, you might read the OSD
map, see an OSD is down, then quickly read the events and find
that the event about the OSD going down is not visible yet (though
it would appear very soon after).

The ``severity`` attribute mainly follows a typical INFO, WARN, ERROR
hierarchy.  However, we have an additional level between INFO and WARN
called RECOVERY.  Where something going bad in the system is usually
a WARN message, the opposite state transition is usually a RECOVERY
message.

This resource supports "more severe than" filtering on the severity
attribute.  Pass the desired severity threshold as a URL parameter
in a GET, such as ``?severity=RECOVERY`` to show everything but INFO.

    """
    serializer_class = EventSerializer

    @property
    def queryset(self):
        return self.session.query(Event).order_by(Event.when.desc())

    def _filter_by_severity(self, request, queryset=None):
        if queryset is None:
            queryset = self.queryset
        severity_str = request.GET.get("severity", "INFO")
        try:
            severity = severity_from_str(severity_str)
        except KeyError:
            raise ParseError("Invalid severity '%s', must be on of %s" % (severity_str,
                                                                          ",".join(SEVERITIES.values())))

        return queryset.filter(Event.severity <= severity)

    def list(self, request):
        return Response(self._paginate(request, self._filter_by_severity(request)))

    def list_cluster(self, request, fsid):
        return Response(self._paginate(request, self._filter_by_severity(request, self.queryset.filter_by(fsid=fsid))))

    def list_server(self, request, fqdn):
        return Response(self._paginate(request, self._filter_by_severity(request, self.queryset.filter_by(fqdn=fqdn))))


class LogTailViewSet(RPCViewSet):
    """
A primitive remote log viewer.

Logs are retrieved on demand from the Ceph servers, so this resource will return a 503 error if no suitable
server is available to get the logs.

GETs take an optional ``lines`` parameter for the number of lines to retrieve.
    """
    serializer_class = LogTailSerializer

    def get_cluster_log(self, request, fsid):
        """
        Retrieve the cluster log from one of a cluster's mons (expect it to be in /var/log/ceph/ceph.log)
        """

        lines = request.GET.get('lines', 40)

        # Resolve FSID to name
        name = self.client.get_cluster(fsid)['name']

        # Resolve FSID to list of mon FQDNs
        servers = self.client.server_list_cluster(fsid)
        # Sort to get most recently contact server first
        servers = sorted(servers,
                         lambda a, b: cmp(dateutil_parse(b['last_contact']), dateutil_parse(a['last_contact'])))
        mon_fqdns = []
        for server in servers:
            for service in server['services']:
                service_id = ServiceId(*(service['id']))
                if service['running'] and service_id.service_type == MON and service_id.fsid == fsid:
                    mon_fqdns.append(server['fqdn'])

        client = salt.client.LocalClient(config.get('cthulhu', 'salt_config_path'))
        log.debug("LogTailViewSet: mons for %s are %s" % (fsid, mon_fqdns))
        # For each mon FQDN, try to go get ceph/$cluster.log, if we succeed return it, if we fail try the next one
        # NB this path is actually customizable in ceph as `mon_cluster_log_file` but we assume user hasn't done that.
        for mon_fqdn in mon_fqdns:
            results = client.cmd(mon_fqdn, "log_tail.tail", ["ceph/{name}.log".format(name=name), lines])
            if results:
                return Response({'lines': results[mon_fqdn]})
            else:
                log.info("Failed to get log from %s" % mon_fqdn)

        # If none of the mons gave us what we wanted, return a 503 service unavailable
        return Response("mon log data unavailable", status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def list_server_logs(self, request, fqdn):
        client = salt.client.LocalClient(config.get('cthulhu', 'salt_config_path'))
        results = client.cmd(fqdn, "log_tail.list_logs", ["."])
        if not results:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response(sorted(results[fqdn]))

    def get_server_log(self, request, fqdn, log_path):
        lines = request.GET.get('lines', 40)

        client = salt.client.LocalClient(config.get('cthulhu', 'salt_config_path'))
        results = client.cmd(fqdn, "log_tail.tail", [log_path, lines])
        if not results:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
            return Response({'lines': results[fqdn]})


class MonViewSet(RPCViewSet):
    """
Ceph monitor services.

Note that the ID used to retrieve a specific mon using this API resource is
the monitor *name* as opposed to the monitor *rank*.

The quorum status reported here is based on the last mon status reported by
the Ceph cluster, and also the status of each mon daemon queried by Calamari.

For debugging mons which are failing to join the cluster, it may be
useful to show users data from the /status sub-url, which returns the
"mon_status" output from the daemon.

    """
    serializer_class = MonSerializer

    def _get_mons(self, fsid):
        mon_status = self.client.get_sync_object(fsid, 'mon_status')
        if not mon_status:
            raise Http404("No mon data available")

        mons = mon_status['monmap']['mons']
        service_ids = [ServiceId(fsid, MON, mon['name']) for mon in mons]
        services_info = self.client.status_by_service(service_ids)

        # Use this to invalidate any statuses we can prove are outdated
        lowest_valid_epoch = mon_status['election_epoch']

        # Step 1: account for the possibility that our cluster-wide mon_status object
        # could be out of date with respect to local mon_status data that we get
        # from each mon service.
        for mon, service_info in zip(mons, services_info):
            if service_info and service_info['status']:
                local_epoch = service_info['status']['election_epoch']
                if local_epoch > lowest_valid_epoch:
                    # Evidence that the cluster mon status is out of date, and we have
                    # a more recent one to replace it with.
                    log.warn("Using mon '%s' local status as it is most recent" % (mon['name']))
                    mon_status = service_info['status']
                    lowest_valid_epoch = mon_status['election_epoch']
                elif local_epoch == lowest_valid_epoch and service_info['status']['quorum'] != mon_status['quorum']:
                    # Evidence that the cluster mon status is out of date, and we
                    # have to assume that anyone it claimed was in quorum no longer is.
                    log.warn("Disregarding cluster mon status because '%s' disagrees" % (mon['name']))
                    lowest_valid_epoch = local_epoch + 1

        # Step 2: Reconcile what the cluster mon status thinks about this mon with
        # what it thinks about itself.
        for mon, service_info in zip(mons, services_info):
            mon['server'] = service_info['server'] if service_info else None

            cluster_opinion = mon['rank'] in mon_status['quorum'] and mon_status['election_epoch'] >= lowest_valid_epoch
            if service_info is None or service_info['status'] is None:
                # Handle local data being unavailable, e.g. if our agent
                # is not installed on one or more mons
                mon['status'] = None
                mon['in_quorum'] = cluster_opinion
                continue

            status = service_info['status']
            mon['status'] = status

            local_opinion = service_info['running'] and (status['rank'] in status['quorum']) and \
                status['election_epoch'] >= lowest_valid_epoch

            if cluster_opinion != local_opinion:
                log.warn("mon %s/%s local state disagrees with cluster state" % (mon['name'], mon['rank']))

                if status['election_epoch'] == 0 or not service_info['running']:
                    # You're claiming not to be in quorum, I believe you because I have
                    # no way of knowing the cluster map is more up to date than your info.
                    mon['in_quorum'] = local_opinion
                elif status['election_epoch'] < mon_status['election_epoch']:
                    # The cluster map is unambiguously more up to date than your info, so
                    # I believe it.
                    mon['in_quorum'] = cluster_opinion
                else:
                    # Your data is newer than the cluster map, I believe you.
                    mon['in_quorum'] = local_opinion
            else:
                mon['in_quorum'] = cluster_opinion

        # Step 3: special case, handle when our local inferrences about mon status
        # make it impossible for us to believe what the cluster mon status is telling us.
        if len([m for m in mons if m['in_quorum']]) < (len(mons) / 2 + 1):
            log.warn("Asserting that there is no quorum even if cluster map says there is")
            # I think the cluster map is lying about there being a quorum at all
            for m in mons:
                m['in_quorum'] = False

        return mons

    def retrieve(self, request, fsid, mon_id):
        mons = self._get_mons(fsid)
        try:
            mon = [m for m in mons if m['name'] == mon_id][0]
        except IndexError:
            raise Http404("Mon '%s' not found" % mon_id)

        return Response(self.serializer_class(DataObject(mon)).data)

    def retrieve_status(self, request, fsid, mon_id):
        service_info = self.client.status_by_service([ServiceId(fsid, 'mon', mon_id)])[0]
        if service_info is None:
            raise Http404("Mon not found '%s'" % mon_id)

        return Response(service_info['status'])

    def list(self, request, fsid):
        return Response(self.serializer_class([DataObject(m) for m in self._get_mons(fsid)], many=True).data)
