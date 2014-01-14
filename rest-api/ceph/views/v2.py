from collections import defaultdict
import logging

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from django.contrib.auth.decorators import login_required

from ceph.serializers.v2 import PoolSerializer, CrushRuleSetSerializer, CrushRuleSerializer, \
    ServerSerializer, SimpleServerSerializer, SaltKeySerializer, RequestSerializer, \
    SyncObjectSerializer, ClusterSerializer

from ceph.views.rpc_view import RPCViewSet, DataObject, RPCView
from ceph.views.v1 import _get_local_grains
from cthulhu.manager.types import CRUSH_RULE, POOL

from cthulhu.config import CalamariConfig

config = CalamariConfig()

log = logging.getLogger('django.request')


@api_view(['GET'])
@login_required
def grains(request):
    """
The salt grains for the host running Calamari server.  These are variables
from Saltstack that tell us useful properties of the host.
    """
    return Response(_get_local_grains())


class RequestViewSet(RPCViewSet):
    """
Calamari server requests, tracking long-running operations on the Calamari server.  Some
API resources return a ``204 ACCEPTED`` response with a request ID, which you can use with
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


class PoolViewSet(RPCViewSet):
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
            return Response(create_response)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, fsid, pool_id):
        delete_response = self.client.delete(fsid, POOL, int(pool_id))
        return Response(delete_response)

    def update(self, request, fsid, pool_id):
        updates = request.DATA
        # TODO: validation, but we don't want to check all fields are present (because
        # this is a PATCH), just that those present are valid.  rest_framework serializer
        # may or may not be able to do that out the box.
        return Response(self.client.update(fsid, POOL, int(pool_id), updates))


class SyncObject(RPCView):
    """
These objects are the raw data received by the Calamari server from the Ceph cluster,
such as the cluster maps
    """
    serializer_class = SyncObjectSerializer

    def get(self, request, fsid, sync_type):
        obj = DataObject({'data': self.client.get_sync_object(fsid, sync_type)})
        return Response(SyncObjectSerializer(obj).data)


class DerivedObject(RPCView):
    """
These objects are generated by Calamari server in response to cluster maps,
to provide more convenient or high level representations of the cluster state.
    """
    # FIXME: just using SyncObjectSerializer because it's a 'data' wrapper,
    # should really avoid a Serializer at all and just return the data
    serializer_class = SyncObjectSerializer

    def get(self, request, fsid, derived_type):
        obj = DataObject({'data': self.client.get_derived_object(fsid, derived_type)})
        return Response(SyncObjectSerializer(obj).data)


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
