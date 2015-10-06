from collections import defaultdict
from dateutil.parser import parse as dateutil_parse
import logging
import shlex

from django.http import Http404
from rest_framework.exceptions import ParseError, APIException, PermissionDenied
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status

from calamari_rest.parsers.v2 import CrushMapParser

from calamari_common.remote import get_remote

from calamari_rest.serializers.v2 import PoolSerializer, CrushRuleSetSerializer, CrushRuleSerializer, \
    ServerSerializer, SimpleServerSerializer, SaltKeySerializer, RequestSerializer, \
    ClusterSerializer, EventSerializer, LogTailSerializer, OsdSerializer, ConfigSettingSerializer, MonSerializer, OsdConfigSerializer, \
    CliSerializer, CrushNodeSerializer, CrushTypeSerializer
from calamari_rest.views.database_view_set import DatabaseViewSet
from calamari_rest.views.exceptions import ServiceUnavailable
from calamari_rest.views.paginated_mixin import PaginatedMixin
from rest_framework.permissions import IsAuthenticated
from calamari_rest.views.remote_view_set import RemoteViewSet
from calamari_rest.views.rpc_view import RPCViewSet, DataObject
from calamari_rest.permissions import IsRoleAllowed
from calamari_rest.views.crush_node import lookup_ancestry
from calamari_common.config import CalamariConfig
from calamari_common.types import CRUSH_MAP, CRUSH_RULE, CRUSH_NODE, CRUSH_TYPE, POOL, OSD, USER_REQUEST_COMPLETE, USER_REQUEST_SUBMITTED, \
    OSD_IMPLEMENTED_COMMANDS, MON, OSD_MAP, SYNC_OBJECT_TYPES, ServiceId, severity_from_str, SEVERITIES

from django.views.decorators.csrf import csrf_exempt

try:
    from calamari_common.db.event import Event
except ImportError:
    # No database available
    class Event(object):
        pass


remote = get_remote()

config = CalamariConfig()

log = logging.getLogger('django.request')

if log.level <= logging.DEBUG:
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    for handler in log.handlers:
        logging.getLogger('sqlalchemy.engine').addHandler(handler)


@permission_classes((IsAuthenticated, IsRoleAllowed))
@api_view(['GET'])
def grains(request):
    """
The salt grains for the host running Calamari server.  These are variables
from Saltstack that tell us useful properties of the host.

The fields in this resource are passed through verbatim from SaltStack, see
the examples for which fields are available.
    """
    return Response(remote.get_local_metadata())


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

To cancel a request while it is running, send an empty POST to ``request/<request id>/cancel``.
    """
    serializer_class = RequestSerializer

    def cancel(self, request, request_id):
        user_request = DataObject(self.client.cancel_request(request_id))
        return Response(self.serializer_class(user_request).data)

    def retrieve(self, request, **kwargs):
        request_id = kwargs['request_id']
        user_request = DataObject(self.client.get_request(request_id))
        return Response(self.serializer_class(user_request).data)

    def list(self, request, **kwargs):
        fsid = kwargs.get('fsid', None)
        filter_state = request.GET.get('state', None)
        valid_states = [USER_REQUEST_COMPLETE, USER_REQUEST_SUBMITTED]
        if filter_state is not None and filter_state not in valid_states:
            raise ParseError("State must be one of %s" % ", ".join(valid_states))

        requests = self.client.list_requests({'state': filter_state, 'fsid': fsid})
        return Response(self._paginate(request, requests))


class CrushMapViewSet(RPCViewSet):
    """
Allows retrieval and replacement of a crushmap as a whole
    """
    parser_classes = (CrushMapParser,)

    def retrieve(self, request, fsid):
        crush_map = self.client.get_sync_object(fsid, 'osd_map')['crush_map_text']
        return Response(crush_map)

    def replace(self, request, fsid):
        return Response(self.client.update(fsid, CRUSH_MAP, None, request.DATA))


class CrushNodeViewSet(RPCViewSet):
    """
The CRUSH algorithm distributes data objects among storage devices according to a per-device weight value, approximating a uniform probability distribution. CRUSH distributes objects and their replicas according to the hierarchical cluster map you define. Your CRUSH map represents the available storage devices and the logical elements that contain them.
    """

    serializer_class = CrushNodeSerializer

    def create(self, request, fsid):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid(request.method):

            # TODO semantic validation
            # type exists, name and id are unique
            create_response = self.client.create(fsid, CRUSH_NODE, serializer.get_data())
            # TODO: handle case where the creation is rejected for some reason (should
            # be passed an errors dict for a clean failure, or a zerorpc exception
            # for a dirty failure)
            assert 'request_id' in create_response
            return Response(create_response, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, fsid):
        crush_nodes = self.client.list(fsid, CRUSH_NODE, {})
        return Response(self.serializer_class(crush_nodes).data)

    def retrieve(self, request, fsid, node_id):
        crush_node = self.client.get(fsid, CRUSH_NODE, int(node_id))
        if crush_node:
            return Response(self.serializer_class(DataObject(crush_node)).data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, fsid, node_id):
        delete_response = self.client.delete(fsid, CRUSH_NODE, int(node_id), status=status.HTTP_202_ACCEPTED)
        return Response(delete_response, status=status.HTTP_202_ACCEPTED)

    def update(self, request, fsid, node_id):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid(request.method):
            updates = serializer.get_data()

            response = self.client.update(fsid, CRUSH_NODE, int(node_id), updates)
            assert 'request_id' in response
            return Response(response, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CrushRuleViewSet(RPCViewSet):
    """
A CRUSH ruleset is a collection of CRUSH rules which are applied
together to a pool.
    """
    serializer_class = CrushRuleSerializer

    def list(self, request, fsid):
        rules = self.client.list(fsid, CRUSH_RULE, {})
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
        rules = self.client.list(fsid, CRUSH_RULE, {})
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


class CrushTypeViewSet(RPCViewSet):
    """
By default these include root, datacenter, room, row, pod, pdu, rack, chassis and host, but those types can be customized to be anything appropriate by modifying the CRUSH map.
By convention, there is one leaf bucket type and it is type 0; however, you may give it any name you like (e.g., osd, disk, drive, storage, etc.)
    """
    serializer_class = CrushTypeSerializer

    def list(self, request, fsid):
        crush_types = self.client.list(fsid, CRUSH_TYPE, {})
        return Response(self.serializer_class(crush_types).data)

    def retrieve(self, request, fsid, type_id):
        crush_type = self.client.get(fsid, CRUSH_TYPE, int(type_id))
        return Response(self.serializer_class(DataObject(crush_type)).data)


class SaltKeyViewSet(RPCViewSet):
    """
Ceph servers authentication with the Calamari using a key pair.  Before
Calamari accepts messages from a server, the server's key must be accepted.
    """
    serializer_class = SaltKeySerializer

    def list(self, request):
        return Response(self.serializer_class(self.client.minion_status(None), many=True).data)

    def partial_update(self, request, minion_id):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid(request.method):
            self._partial_update(minion_id, serializer.get_data())
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _partial_update(self, minion_id, data):
        valid_status = ['accepted', 'rejected']
        if 'status' not in data:
            raise ParseError({'status': "This field is mandatory"})
        elif data['status'] not in valid_status:
            raise ParseError({'status': "Must be one of %s" % ",".join(valid_status)})
        else:
            key = self.client.minion_get(minion_id)
            transition = [key['status'], data['status']]
            if transition == ['pre', 'accepted']:
                self.client.minion_accept(minion_id)
            elif transition == ['pre', 'rejected']:
                self.client.minion_reject(minion_id)
            else:
                raise ParseError({'status': ["Transition {0}->{1} is invalid".format(
                    transition[0], transition[1]
                )]})

    def _validate_list(self, request):
        keys = request.DATA
        if not isinstance(keys, list):
            raise ParseError("Bulk PATCH must send a list")
        for key in keys:
            if 'id' not in key:
                raise ParseError("Items in bulk PATCH must have 'id' attribute")

    def list_partial_update(self, request):
        self._validate_list(request)

        keys = request.DATA
        log.debug("KEYS %s" % keys)
        for key in keys:
            self._partial_update(key['id'], key)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, minion_id):
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
        # Issue overlapped RPCs first
        ceph_config = self.client.get_sync_object(fsid, 'config', async=True)
        rules = self.client.list(fsid, CRUSH_RULE, {}, async=True)
        ceph_config = ceph_config.get()
        rules = rules.get()

        if not ceph_config:
            return Response("Cluster configuration unavailable", status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if not rules:
            return Response("No CRUSH rules exist, pool creation is impossible",
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Ceph does not reliably inform us of a default ruleset that exists, so we check
        # what it tells us against the rulesets we know about.
        ruleset_ids = sorted(list(set([r['ruleset'] for r in rules])))
        if int(ceph_config['osd_pool_default_crush_rule']) in ruleset_ids:
            # This is the ceph<0.80 setting
            default_ruleset = ceph_config['osd_pool_default_crush_rule']
        elif int(ceph_config.get('osd_pool_default_crush_replicated_ruleset', -1)) in ruleset_ids:
            # This is the ceph>=0.80
            default_ruleset = ceph_config['osd_pool_default_crush_replicated_ruleset']
        else:
            # Ceph may have an invalid default set which
            # would cause undefined behaviour in pool creation (#8373)
            # In this case, pick lowest numbered ruleset as default
            default_ruleset = ruleset_ids[0]

        defaults = NullableDataObject({
            'size': int(ceph_config['osd_pool_default_size']),
            'crush_ruleset': int(default_ruleset),
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

        pools = [PoolDataObject(p) for p in self.client.list(fsid, POOL, {})]
        return Response(PoolSerializer(pools, many=True).data)

    def retrieve(self, request, fsid, pool_id):
        pool = PoolDataObject(self.client.get(fsid, POOL, int(pool_id)))
        return Response(PoolSerializer(pool).data)

    def create(self, request, fsid):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid(request.method):
            response = self._validate_semantics(fsid, None, serializer.get_data())
            if response is not None:
                return response

            create_response = self.client.create(fsid, POOL, serializer.get_data())

            # TODO: handle case where the creation is rejected for some reason (should
            # be passed an errors dict for a clean failure, or a zerorpc exception
            # for a dirty failure)
            assert 'request_id' in create_response
            return Response(create_response, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, fsid, pool_id):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid(request.method):
            response = self._validate_semantics(fsid, pool_id, serializer.get_data())
            if response is not None:
                return response

            return self._return_request(self.client.update(fsid, POOL, int(pool_id), serializer.get_data()))
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, fsid, pool_id):
        delete_response = self.client.delete(fsid, POOL, int(pool_id), status=status.HTTP_202_ACCEPTED)
        return Response(delete_response, status=status.HTTP_202_ACCEPTED)

    def _validate_semantics(self, fsid, pool_id, data):
        errors = defaultdict(list)
        self._check_name_unique(fsid, pool_id, data, errors)
        self._check_crush_ruleset(fsid, data, errors)
        self._check_pgp_less_than_pg_num(data, errors)
        self._check_pg_nums_dont_decrease(fsid, pool_id, data, errors)
        self._check_pg_num_inside_config_bounds(fsid, data, errors)

        if errors.items():
            if 'name' in errors:
                return Response(errors, status=status.HTTP_409_CONFLICT)
            else:
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def _check_pg_nums_dont_decrease(self, fsid, pool_id, data, errors):
        if pool_id is not None:
            detail = self.client.get(fsid, POOL, int(pool_id))
            for field in ['pg_num', 'pgp_num']:
                expanded_field = 'pg_placement_num' if field == 'pgp_num' else 'pg_num'
                if field in data and data[field] < detail[expanded_field]:
                    errors[field].append('must be >= than current {field}'.format(field=field))

    def _check_crush_ruleset(self, fsid, data, errors):
        if 'crush_ruleset' in data:
            rules = self.client.list(fsid, CRUSH_RULE, {})
            rulesets = set(r['ruleset'] for r in rules)
            if data['crush_ruleset'] not in rulesets:
                errors['crush_ruleset'].append("CRUSH ruleset {0} not found".format(data['crush_ruleset']))

    def _check_pg_num_inside_config_bounds(self, fsid, data, errors):
        ceph_config = self.client.get_sync_object(fsid, 'config')
        if not ceph_config:
            return Response("Cluster configuration unavailable", status=status.HTTP_503_SERVICE_UNAVAILABLE)
        if 'pg_num' in data and data['pg_num'] > int(ceph_config['mon_max_pool_pg_num']):
            errors['pg_num'].append('requested pg_num must be <= than current limit of {max}'.format(max=ceph_config['mon_max_pool_pg_num']))

    def _check_pgp_less_than_pg_num(self, data, errors):
        if 'pgp_num' in data and 'pg_num' in data and data['pg_num'] < data['pgp_num']:
            errors['pgp_num'].append('must be >= to pg_num')

    def _check_name_unique(self, fsid, pool_id, data, errors):
        pool_name_to_id = dict([(x.pool_name, x.pool) for x in [PoolDataObject(p) for p in self.client.list(fsid, POOL, {})]])
        if pool_name_to_id.get(data.get('name')) not in (None, pool_id):
            errors['name'].append('Pool with name {name} already exists'.format(name=data['name']))


class OsdViewSet(RPCViewSet, RequestReturner):
    """
Manage Ceph OSDs.

Apply ceph commands to an OSD by doing a POST with no data to
api/v2/cluster/<fsid>/osd/<osd_id>/command/<command>
where <command> is one of ("scrub", "deep-scrub", "repair")

e.g. Initiate a scrub on OSD 0 by POSTing {} to api/v2/cluster/<fsid>/osd/0/command/scrub

Filtering is available on this resource:

::

    # Pass a ``pool`` URL parameter set to a pool ID to filter by pool, like this:
    /api/v2/cluster/<fsid>/osd?pool=1

    # Pass a series of ``id__in[]`` parameters to specify a list of OSD IDs
    # that you wish to receive.
    /api/v2/cluster/<fsid>/osd?id__in[]=2&id__in[]=3

    """
    serializer_class = OsdSerializer

    def list(self, request, fsid):
        # Get data needed for filtering
        list_filter = {}

        if 'pool' in request.GET:
            try:
                pool_id = int(request.GET['pool'])
            except ValueError:
                return Response("Pool ID must be an integer", status=status.HTTP_400_BAD_REQUEST)
            list_filter['pool'] = pool_id

        if 'id__in[]' in request.GET:
            try:
                ids = request.GET.getlist("id__in[]")
                list_filter['id__in'] = [int(i) for i in ids]
            except ValueError:
                return Response("Invalid OSD ID in list", status=status.HTTP_400_BAD_REQUEST)

        # Get data
        osds = self.client.list(fsid, OSD, list_filter, async=True)
        parent_map = self.client.get_sync_object(fsid, 'osd_map', ['parent_bucket_by_node_id'], async=True)
        osd_to_pools = self.client.get_sync_object(fsid, 'osd_map', ['osd_pools'], async=True)
        crush_nodes = self.client.get_sync_object(fsid, 'osd_map', ['osd_tree_node_by_id'], async=True)
        osd_metadata = self.client.get_sync_object(fsid, 'osd_map', ['metadata_by_id'], async=True)
        osds = osds.get()

        # Get data depending on OSD list
        server_info = self.client.server_by_service([ServiceId(fsid, OSD, str(osd['osd'])) for osd in osds], async=True)
        osd_commands = self.client.get_valid_commands(fsid, OSD, [x['osd'] for x in osds], async=True)

        # Preparation complete, await all data to serialize result
        parent_map = parent_map.get()
        osd_to_pools = osd_to_pools.get()
        crush_nodes = crush_nodes.get()
        osd_metadata = osd_metadata.get()
        server_info = server_info.get()
        osd_commands = osd_commands.get()

        # Build OSD data objects
        for o in osds:
            # An OSD being in the OSD map does not guarantee its presence in the CRUSH
            # map, as "osd crush rm" and "osd rm" are separate operations.
            try:
                o.update({'reweight': float(crush_nodes[o['osd']]['reweight'])})
            except KeyError:
                log.warning("No CRUSH data available for OSD {0}".format(o['osd']))
                o.update({'reweight': 0.0})

        for o, (service_id, fqdn) in zip(osds, server_info):
            o['server'] = fqdn

        for o in osds:
            o['pools'] = osd_to_pools[o['osd']]
            try:
                o['backend_device_node'] = osd_metadata[o['osd']]['backend_filestore_dev_node']
            except KeyError:
                o['backend_device_node'] = None
            try:
                o['backend_partition_path'] = osd_metadata[o['osd']]['backend_filestore_partition_path']
            except KeyError:
                o['backend_partition_path'] = None
            o.update(osd_commands[o['osd']])
            o.update({'crush_node_ancestry': lookup_ancestry(o['osd'], parent_map)})

        return Response(self.serializer_class([DataObject(o) for o in osds], many=True).data)

    @csrf_exempt
    def retrieve(self, request, fsid, osd_id):
        osd = self.client.get_sync_object(fsid, 'osd_map', ['osds_by_id', int(osd_id)])
        crush_node = self.client.get_sync_object(fsid, 'osd_map', ['osd_tree_node_by_id', int(osd_id)])
        osd['reweight'] = float(crush_node['reweight'])
        osd['server'] = self.client.server_by_service([ServiceId(fsid, OSD, osd_id)])[0][1]

        pools = self.client.get_sync_object(fsid, 'osd_map', ['osd_pools', int(osd_id)])
        osd['pools'] = pools

        osd_metadata = self.client.get_sync_object(fsid, 'osd_map', ['metadata_by_id', int(osd_id)])
        try:
            osd['backend_device_node'] = osd_metadata['backend_filestore_dev_node']
        except KeyError:
            osd['backend_device_node'] = None
        try:
            osd['backend_partition_path'] = osd_metadata['backend_filestore_partition_path']
        except KeyError:
            osd['backend_partition_path'] = None

        osd_commands = self.client.get_valid_commands(fsid, OSD, [int(osd_id)])
        osd.update(osd_commands[int(osd_id)])
        parent_map = self.client.get_sync_object(fsid, 'osd_map', ['parent_bucket_by_node_id'])
        osd.update({'crush_node_ancestry': lookup_ancestry(osd['osd'], parent_map)})

        return Response(self.serializer_class(DataObject(osd)).data)

    def update(self, request, fsid, osd_id):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid(request.method):
            return self._return_request(self.client.update(fsid, OSD, int(osd_id), serializer.get_data()))
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

        serializer = self.serializer_class(data=request.DATA)
        if not serializer.is_valid(request.method):
            return Response(serializer.errors, status=403)

        response = self.client.update(fsid, OSD_MAP, None, serializer.get_data())

        return self._return_request(response)


class SyncObject(RPCViewSet):
    """
These objects are the raw data received by the Calamari server from the Ceph cluster,
such as the cluster maps
    """

    def retrieve(self, request, fsid, sync_type):
        return Response(self.client.get_sync_object(fsid, sync_type))

    def describe(self, request, fsid):
        return Response([s.str for s in SYNC_OBJECT_TYPES])


class DebugJob(RPCViewSet, RequestReturner):
    """
For debugging and automated testing only.
    """
    def create(self, request, fqdn):
        cmd = request.DATA['cmd']
        args = request.DATA['args']

        # Avoid this debug interface being an arbitrary execution mechanism.
        if not cmd.startswith("ceph.selftest"):
            raise PermissionDenied("Command '%s' is not a self test command".format(cmd))

        return self._return_request(self.client.debug_job(fqdn, cmd, args))


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

    def _addr_to_iface(self, addr, ip_interfaces):
        """
        Resolve an IP address to a network interface.

        :param addr: An address string like "1.2.3.4"
        :param ip_interfaces: The 'ip_interfaces' salt grain
        """
        for iface_name, iface_addrs in ip_interfaces.items():
            if addr in iface_addrs:
                return iface_name

        return None

    def _lookup_ifaces(self, servers):
        """
        Resolve the frontend/backend addresses (known
        by cthulhu via Ceph) to network interfaces (known by salt from its
        grains).
        """
        server_to_grains = remote.get_remote_metadata([s['fqdn'] for s in servers])

        for server in servers:
            fqdn = server['fqdn']
            grains = server_to_grains[fqdn]
            server['frontend_iface'] = None
            server['backend_iface'] = None
            if grains is None:
                # No metadata available for this server
                continue
            else:
                try:
                    if server['frontend_addr']:
                        server['frontend_iface'] = self._addr_to_iface(server['frontend_addr'], grains['ip_interfaces'])
                    if server['backend_addr']:
                        server['backend_iface'] = self._addr_to_iface(server['backend_addr'], grains['ip_interfaces'])
                except KeyError:
                    # Expected network metadata not available, we cannot infer
                    # front/back interfaces so leave them null
                    pass

    def list(self, request, fsid):
        servers = self.client.server_list_cluster(fsid)
        self._lookup_ifaces(servers)
        return Response(self.serializer_class(
            [DataObject(s) for s in servers], many=True).data)

    def retrieve(self, request, fsid, fqdn):
        server = self.client.server_get_cluster(fqdn, fsid)
        self._lookup_ifaces([server])
        return Response(self.serializer_class(DataObject(server)).data)


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
        grains = remote.get_remote_metadata([fqdn])[fqdn]
        if not grains:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(grains)

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


class LogTailViewSet(RemoteViewSet):
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
        # Sort to get most recently contacted server first; drop any
        # for whom last_contact is None
        servers = [s for s in servers if s['last_contact']]
        servers = sorted(servers,
                         key=lambda t: dateutil_parse(t['last_contact']),
                         reverse=True)
        mon_fqdns = []
        for server in servers:
            for service in server['services']:
                service_id = ServiceId(*(service['id']))
                if service['running'] and service_id.service_type == MON and service_id.fsid == fsid:
                    mon_fqdns.append(server['fqdn'])

        log.debug("LogTailViewSet: mons for %s are %s" % (fsid, mon_fqdns))
        # For each mon FQDN, try to go get ceph/$cluster.log, if we succeed return it, if we fail try the next one
        # NB this path is actually customizable in ceph as `mon_cluster_log_file` but we assume user hasn't done that.
        for mon_fqdn in mon_fqdns:
            results = self.client.get_server_log(mon_fqdn, "ceph/{name}.log".format(name=name), lines)
            if results:
                return Response({'lines': results[mon_fqdn]})
            else:
                log.info("Failed to get log from %s" % mon_fqdn)

        # If none of the mons gave us what we wanted, return a 503 service unavailable
        return Response("mon log data unavailable", status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def list_server_logs(self, request, fqdn):
        results = self.client.list_server_logs(fqdn)
        if not results:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response(sorted(results[fqdn]))

    def get_server_log(self, request, fqdn, log_path):
        lines = request.GET.get('lines', 40)
        results = self.client.get_server_log(fqdn, log_path, lines)
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


class CliViewSet(RemoteViewSet):
    """
Access the `ceph` CLI tool remotely.

To achieve the same result as running "ceph osd dump" at a shell, an
API consumer may POST an object in either of the following formats:

::

    {'command': ['osd', 'dump']}

    {'command': 'osd dump'}


The response will be a 200 status code if the command executed, regardless
of whether it was successful, to check the result of the command itself
read the ``status`` attribute of the returned data.

The command will be executed on the first available mon server, retrying
on subsequent mon servers if no response is received.  Due to this retry
behaviour, it is possible for the command to be run more than once in
rare cases; since most ceph commands are idempotent this is usually
not a problem.
    """
    serializer_class = CliSerializer

    def create(self, request, fsid):
        # Validate
        try:
            command = request.DATA['command']
        except KeyError:
            raise ParseError("'command' field is required")
        else:
            if not (isinstance(command, basestring) or isinstance(command, list)):
                raise ParseError("'command' must be a string or list")

        # Parse string commands to list
        if isinstance(command, basestring):
            command = shlex.split(command)

        name = self.client.get_cluster(fsid)['name']
        result = self.run_mon_job(fsid, "ceph.ceph_command", [name, command])
        log.debug("CliViewSet: result = '%s'" % result)

        if not isinstance(result, dict):
            # Errors from salt like "module not available" come back as strings
            raise APIException("Remote error: %s" % str(result))

        return Response(self.serializer_class(DataObject(result)).data)
