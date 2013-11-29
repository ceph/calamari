import threading
import traceback
import zerorpc
from cthulhu.log import log
from cthulhu.manager.types import OsdMap, SYNC_OBJECT_STR_TYPE, OSD, POOL, CLUSTER, CRUSH_RULE


CTHULHU_RPC_URL = 'tcp://127.0.0.1:5050'


class NotFound(Exception):
    def __init__(self, object_type, object_id):
        self.object_type = object_type
        self.object_id = object_id

    def __str__(self):
        return "Object of type %s with id %s not found" % (self.object_type, self.object_id)


class RpcInterface(object):
    def __init__(self, manager):
        self._manager = manager

    def _fs_resolve(self, fs_id):
        try:
            return self._manager.monitors[fs_id]
        except KeyError:
            raise NotFound(CLUSTER, fs_id)

    def _osd_resolve(self, cluster, osd_id):
        osdmap = cluster.get_sync_object(OsdMap)
        if osdmap is None:
            raise NotFound(OSD, osd_id)

        for osd in osdmap['osds']:
            if osd['osd'] == osd_id:
                return osd
        raise NotFound(OSD, osd_id)

    def _pool_resolve(self, cluster, pool_id):
        osdmap = cluster.get_sync_object(OsdMap)
        if osdmap is None:
            raise NotFound(POOL, pool_id)

        for pool in osdmap['pools']:
            if pool['pool'] == pool_id:
                return pool
        raise NotFound(POOL, pool_id)

    def get_cluster(self, fs_id):
        """
        Returns a dict, or None if not found
        """
        try:
            cluster = self._manager.monitors[fs_id]
        except KeyError:
            return None
        else:
            return {
                'id': cluster.fsid,
                'name': cluster.name,
                'update_time': cluster.update_time.isoformat()
            }

    def list_clusters(self):
        result = []
        for fsid in self._manager.monitors.keys():
            result.append(self.get_cluster(fsid))
        return result

    def delete_cluster(self, fs_id):
        self._manager.delete_cluster(fs_id)

    def get_sync_object(self, fs_id, object_type):
        """
        Get one of the objects that ClusterMonitor keeps a copy of from the mon, such
        as the cluster maps.

        :param fs_id: The fsid of a cluster
        :param object_type: String, one of SYNC_OBJECT_TYPES
        """
        return self._fs_resolve(fs_id).get_sync_object(SYNC_OBJECT_STR_TYPE[object_type])

    def get_derived_object(self, fs_id, object_type):
        """
        Get one of the objects that ClusterMonitor generates from the sync objects, typically
        something in a "frontend-friendly" format or augmented with extra info.

        :param fs_id: The fsid of a cluster
        :param object_type: String, name of the derived object
        """
        return self._fs_resolve(fs_id).get_derived_object(object_type)

    def update(self, fs_id, object_type, object_id, attributes):
        """
        Modify an object in a cluster.
        """
        cluster = self._fs_resolve(fs_id)

        if object_type == OSD:
            # Run a resolve to throw exception if it's unknown
            self._osd_resolve(cluster, object_id)
            if not 'id' in attributes:
                attributes['id'] = object_id

            return cluster.request_update(OSD, object_id, attributes)
        elif object_type == POOL:
            if not 'id' in attributes:
                attributes['id'] = object_id

            return cluster.request_update(POOL, object_id, attributes)
        else:
            raise NotImplementedError(object_type)

    def create(self, fs_id, object_type, attributes):
        """
        Create a new object in a cluster
        """
        cluster = self._fs_resolve(fs_id)

        if object_type == POOL:
            return cluster.request_create(POOL, attributes)
        else:
            raise NotImplementedError(object_type)

    def delete(self, fs_id, object_type, object_id):
        cluster = self._fs_resolve(fs_id)

        if object_type == POOL:
            return cluster.request_delete(POOL, object_id)
        else:
            raise NotImplementedError(object_type)

    def get(self, fs_id, object_type, object_id):
        """
        Get one object from a particular cluster.
        """

        cluster = self._fs_resolve(fs_id)
        if object_type == OSD:
            return self._osd_resolve(cluster, object_id)
        elif object_type == POOL:
            return self._pool_resolve(cluster, object_id)
        else:
            raise NotImplementedError(object_type)

    def list(self, fs_id, object_type):
        """
        Get many objects
        """

        cluster = self._fs_resolve(fs_id)
        if object_type == OSD:
            return cluster.get_sync_object(OsdMap)['osds']
        elif object_type == POOL:
            return cluster.get_sync_object(OsdMap)['pools']
        elif object_type == CRUSH_RULE:
            return cluster.get_sync_object(OsdMap)['crush']['rules']
        else:
            raise NotImplementedError(object_type)

    def get_request(self, fs_id, request_id):
        """
        Get a JSON representation of a UserRequest
        """
        cluster = self._fs_resolve(fs_id)
        request = cluster.get_request(request_id)
        return {
            'id': request.id,
            'state': request.state
        }

    def list_requests(self, fs_id):
        cluster = self._fs_resolve(fs_id)
        requests = cluster.list_requests()
        return [{'id': r.id, 'state': r.state} for r in requests]


class RpcThread(threading.Thread):
    """
    Present a ZeroRPC API for users
    to request state changes.
    """
    def __init__(self, manager):
        super(RpcThread, self).__init__()
        self._manager = manager
        self._complete = threading.Event()
        self._server = zerorpc.Server(RpcInterface(manager))

    def stop(self):
        log.info("%s stopping" % self.__class__.__name__)

        self._complete.set()
        if self._server:
            self._server.stop()

    def run(self):
        try:
            log.info("%s bind..." % self.__class__.__name__)
            self._server.bind(CTHULHU_RPC_URL)
            log.info("%s run..." % self.__class__.__name__)
            self._server.run()
        except:
            log.error(traceback.format_exc())
            raise

        log.info("%s complete..." % self.__class__.__name__)
