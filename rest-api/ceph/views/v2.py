from collections import defaultdict
import logging
from rest_framework.exceptions import ParseError

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from django.contrib.auth.decorators import login_required

from ceph.serializers.v2 import PoolSerializer, CrushRuleSetSerializer, CrushRuleSerializer, \
    ServerSerializer, SimpleServerSerializer, SaltKeySerializer, RequestSerializer, \
    ClusterSerializer, EventSerializer, LogTailSerializer, OsdSerializer
from ceph.views.database_view_set import DatabaseViewSet

from ceph.views.rpc_view import RPCViewSet, DataObject
from ceph.views.v1 import _get_local_grains
from cthulhu.manager.types import CRUSH_RULE, POOL, OSD

from cthulhu.config import CalamariConfig
# FIXME: these imports of cthulhu stuff from the rest layer are too much
from cthulhu.manager.types import SYNC_OBJECT_TYPES
from cthulhu.manager import derived
from cthulhu.persistence.event import Event, severity_from_str, SEVERITIES
import salt.client

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


class RequestViewSet(RPCViewSet):
    """
Calamari server requests, tracking long-running operations on the Calamari server.  Some
API resources return a ``202 ACCEPTED`` response with a request ID, which you can use with
this resource to learn about progress and completion of an operation.
    """
    serializer_class = RequestSerializer

    def retrieve(self, request, fsid, request_id):
        user_request = DataObject(self.client.get_request(fsid, request_id))
        return Response(RequestSerializer(user_request).data)

    def list(self, request, fsid):
        return Response(RequestSerializer([DataObject(r) for r in self.client.list_requests(fsid)], many=True).data)


class CrushRuleViewSet(RPCViewSet):
    """
A CRUSH ruleset is a collection of CRUSH rules which are applied
together to a pool.
    """
    serializer_class = CrushRuleSerializer

    def list(self, request, fsid):
        rules = self.client.list(fsid, CRUSH_RULE)
        return Response(CrushRuleSerializer([DataObject(r) for r in rules], many=True).data)


class CrushRuleSetViewSet(RPCViewSet):
    """
A CRUSH rule is used by Ceph to decide where to locate placement groups on OSDs.
    """
    serializer_class = CrushRuleSetSerializer

    def list(self, request, fsid):
        rules = self.client.list(fsid, CRUSH_RULE)
        rulesets_data = defaultdict(list)
        for rule in rules:
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

    def partial_update(self, request, pk):
        valid_status = ['accepted', 'rejected']
        if not 'status' in request.DATA:
            return Response({'status': "This field is mandatory"}, status=status.HTTP_400_BAD_REQUEST)
        elif request.DATA['status'] not in valid_status:
            return Response({'status': "Must be one of %s" % ",".join(valid_status)},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            if request.DATA['status'] == 'accepted':
                self.client.minion_accept(pk)
            else:
                self.client.minion_reject(pk)

        # TODO validate transitions, cannot go from rejected to accepted.
        # TODO handle 404

        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk):
        # TODO handle 404
        self.client.minion_delete(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, pk):
        return Response(self.serializer_class(self.client.minion_get(pk)).data)


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


class PoolViewSet(RPCViewSet, RequestReturner):
    """
Manage Ceph storage pools.
    """
    serializer_class = PoolSerializer

    def list(self, request, fsid):
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
        self._return_request(self.client.update(fsid, POOL, int(pool_id), updates))


# TODO: filtering on PG state
# TOOD: filtering on up, in
class OsdViewSet(RPCViewSet, RequestReturner):
    """
Manage Ceph OSDs.
    """
    serializer_class = OsdSerializer

    def list(self, request, fsid):
        osds = self.client.get_sync_object(fsid, 'osd_map', ['osds_by_id']).values()
        crush_nodes = self.client.get_sync_object(fsid, 'osd_map', ['osd_tree_node_by_id'])
        for o in osds:
            o.update({'reweight': crush_nodes[o['osd']]['reweight']})
        return Response(self.serializer_class([DataObject(o) for o in osds], many=True).data)

    def retrieve(self, request, fsid, osd_id):
        osd = self.client.get_sync_object(fsid, 'osd_map', ['osds_by_id', int(osd_id)])
        crush_node = self.client.get_sync_object(fsid, 'osd_map', ['osd_tree_node_by_id', int(osd_id)])
        osd['reweight'] = crush_node['reweight']
        return Response(self.serializer_class(DataObject(osd)).data)

    def update(self, request, fsid, osd_id):
        return self._return_request(self.client.update(fsid, OSD, int(osd_id), dict(request.DATA)))


class SyncObject(RPCViewSet):
    """
These objects are the raw data received by the Calamari server from the Ceph cluster,
such as the cluster maps
    """

    def retrieve(self, request, fsid, sync_type):
        return Response(self.client.get_sync_object(fsid, sync_type))

    def describe(self, request, fsid):
        return Response([s.str for s in SYNC_OBJECT_TYPES])


class DerivedObject(RPCViewSet):
    """
These objects are generated by Calamari server in response to cluster maps,
to provide more convenient or high level representations of the cluster state.
    """

    def retrieve(self, request, fsid, derived_type):
        return Response(self.client.get_derived_object(fsid, derived_type))

    def describe(self, request, fsid):
        return Response([p for g in derived.generators for p in g.provides])


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

    def retrieve(self, request, pk):
        return Response(
            self.serializer_class(DataObject(self.client.server_get(pk))).data
        )

    def list(self, request):
        return Response(self.serializer_class([DataObject(s) for s in self.client.server_list()], many=True).data)

    def destroy(self, request, pk):
        self.client.server_delete(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EventViewSet(DatabaseViewSet):
    """
Events generated by Calamari server in response to messages from
servers and Ceph clusters.

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
        mon_fqdns = set()
        for server in servers:
            for service in server['services']:
                if service['running'] and service['id'][1] == 'mon':
                    mon_fqdns.add(server['fqdn'])

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
