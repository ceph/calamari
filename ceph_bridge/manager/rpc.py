import json
import time
import traceback
import uuid

import etcd
import gevent.event

from ceph_bridge.log import log
from ceph_bridge.manager import config
from ceph_bridge.types import CLUSTER
from ceph_bridge.types import CRUSH_MAP
from ceph_bridge.types import CRUSH_NODE
from ceph_bridge.types import CRUSH_RULE
from ceph_bridge.types import CRUSH_TYPE
from ceph_bridge.types import NotFound
from ceph_bridge.types import OSD
from ceph_bridge.types import OSD_MAP
from ceph_bridge.types import OsdMap
from ceph_bridge.types import POOL
from ceph_bridge.types import SERVER
from ceph_bridge.types import ServiceId
from ceph_bridge.types import SYNC_OBJECT_STR_TYPE


class RpcInterface(object):

    def __init__(self, manager):
        self._manager = manager

    def __getattribute__(self, item):
        """Wrap functions with logging

        """
        if item.startswith('_'):
            return object.__getattribute__(self, item)
        else:
            attr = object.__getattribute__(self, item)
            if callable(attr):
                def wrap(*args, **kwargs):
                    log.debug("RpcInterface >> %s(%s, %s)" %
                              (item, args, kwargs))
                    try:
                        rc = attr(*args, **kwargs)
                        log.debug("RpcInterface << %s" % item)
                    except Exception:
                        log.exception("RpcInterface !! %s" % item)
                        raise
                    return rc
                return wrap
            else:
                return attr

    def _fs_resolve(self, fs_id):
        try:
            return self._manager.clusters[fs_id]
        except KeyError:
            raise NotFound(CLUSTER, fs_id)

    def _server_resolve(self, fqdn):
        try:
            return self._manager.servers.get_one(fqdn)
        except KeyError:
            raise NotFound(SERVER, fqdn)

    def _osd_resolve(self, cluster, osd_id):
        osdmap = cluster.get_sync_object(OsdMap)

        try:
            return osdmap.osds_by_id[osd_id]
        except KeyError:
            raise NotFound(OSD, osd_id)

    def _pool_resolve(self, cluster, pool_id):
        osdmap = cluster.get_sync_object(OsdMap)

        try:
            return osdmap.pools_by_id[pool_id]
        except KeyError:
            raise NotFound(POOL, pool_id)

    def get_cluster(self, fs_id):
        """Returns a dict, or None if not found

        """
        try:
            cluster = self._manager.clusters[fs_id]
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
        for fsid in self._manager.clusters.keys():
            result.append(self.get_cluster(fsid))
        return result

    def delete_cluster(self, fs_id):
        # Clear out records of services belonging to the cluster
        self._manager.servers.delete_cluster(fs_id)
        # Clear out records of the cluster itself
        self._manager.delete_cluster(fs_id)

    def get_sync_object(self, fs_id, object_type, path=None):
        """Get one of the objects that ClusterMonitor keeps a copy of from

        the mon, such as the cluster maps.

        :param fs_id: The fsid of a cluster

        :param object_type: String, one of SYNC_OBJECT_TYPES

        :param path: List, optional, a path within the object to return

        instead of the whole thing

        :return: the requested data, or None if it was not found

        (including if any element of ``path``

                 was not found)

        """

        if path:
            obj = self._fs_resolve(fs_id).get_sync_object(
                SYNC_OBJECT_STR_TYPE[object_type])
            try:
                for part in path:
                    if isinstance(obj, dict):
                        obj = obj[part]
                    else:
                        obj = getattr(obj, part)
            except (AttributeError, KeyError) as e:
                log.exception("Exception %s traversing %s: obj=%s" %
                              (e, path, obj))
                raise NotFound(object_type, path)
            return obj
        else:
            return self._fs_resolve(
                fs_id).get_sync_object_data(SYNC_OBJECT_STR_TYPE[object_type]
                                            )

    def update(self, fs_id, object_type, object_id, attributes):
        """Modify an object in a cluster.

        """
        cluster = self._fs_resolve(fs_id)

        if object_type == OSD:
            # Run a resolve to throw exception if it's unknown
            self._osd_resolve(cluster, object_id)
            if 'id' not in attributes:
                attributes['id'] = object_id

            return cluster.request_update('update', OSD, object_id, attributes)
        elif object_type == POOL:
            self._pool_resolve(cluster, object_id)
            if 'id' not in attributes:
                attributes['id'] = object_id

            return cluster.request_update(
                'update', POOL, object_id, attributes
            )
        elif object_type == OSD_MAP:
            return cluster.request_update(
                'update_config', OSD, object_id, attributes
            )

        elif object_type == CRUSH_MAP:
            return cluster.request_update(
                'update', CRUSH_MAP, object_id, attributes
            )

        elif object_type == CRUSH_NODE:
            return cluster.request_update(
                'update', CRUSH_NODE, object_id, attributes
            )

        else:
            raise NotImplementedError(object_type)

    def apply(self, fs_id, object_type, object_id, command):
        """Apply commands that do not modify an object in a cluster.

        """
        cluster = self._fs_resolve(fs_id)

        if object_type == OSD:
            # Run a resolve to throw exception if it's unknown
            self._osd_resolve(cluster, object_id)
            return cluster.request_apply(OSD, object_id, command)

        else:
            raise NotImplementedError(object_type)

    def get_valid_commands(self, fs_id, object_type, object_ids):
        """Determine what commands can be run on OSD object_ids

        """
        if object_type != OSD:
            raise NotImplementedError(object_type)

        cluster = self._fs_resolve(fs_id)
        try:
            valid_commands = cluster.get_valid_commands(
                object_type, object_ids)
        except KeyError as e:
            raise NotFound(object_type, str(e))

        return valid_commands

    def create(self, fs_id, object_type, attributes):
        """Create a new object in a cluster

        """
        cluster = self._fs_resolve(fs_id)

        if object_type == POOL:
            return cluster.request_create(POOL, attributes)
        elif object_type == CRUSH_NODE:
            return cluster.request_create(CRUSH_NODE, attributes)
        else:
            raise NotImplementedError(object_type)

    def delete(self, fs_id, object_type, object_id):
        cluster = self._fs_resolve(fs_id)

        if object_type == POOL:
            return cluster.request_delete(POOL, object_id)
        elif object_type == CRUSH_NODE:
            return cluster.request_delete(CRUSH_NODE, object_id)
        else:
            raise NotImplementedError(object_type)

    def get(self, fs_id, object_type, object_id):
        """Get one object from a particular cluster.

        """

        cluster = self._fs_resolve(fs_id)
        if object_type == OSD:
            return self._osd_resolve(cluster, object_id)
        elif object_type == POOL:
            return self._pool_resolve(cluster, object_id)
        elif object_type == CRUSH_NODE:
            try:
                crush_node = cluster.get_sync_object(
                    OsdMap).crush_node_by_id[object_id]
            except KeyError:
                raise NotFound(CRUSH_NODE, object_id)
            return crush_node
        elif object_type == CRUSH_TYPE:
            try:
                crush_type = cluster.get_sync_object(
                    OsdMap).crush_type_by_id[object_id]
            except KeyError:
                raise NotFound(CRUSH_TYPE, object_id)
            return crush_type
        else:
            raise NotImplementedError(object_type)

    def list(self, fs_id, object_type, list_filter):
        """Get many objects

        """

        cluster = self._fs_resolve(fs_id)
        osd_map = cluster.get_sync_object_data(OsdMap)
        if osd_map is None:
            return []
        if object_type == OSD:
            result = osd_map['osds']
            if 'id__in' in list_filter:
                result = [o for o in result if o[
                    'osd'] in list_filter['id__in']]
            if 'pool' in list_filter:
                try:
                    osds_in_pool = cluster.get_sync_object(
                        OsdMap).osds_by_pool[
                            list_filter['pool']
                    ]
                except KeyError:
                    raise NotFound(
                        "Pool {0} does not exist".format(list_filter['pool']))
                else:
                    result = [o for o in result if o['osd'] in osds_in_pool]

            return result
        elif object_type == POOL:
            return osd_map['pools']
        elif object_type == CRUSH_RULE:
            return osd_map['crush']['rules']
        elif object_type == CRUSH_NODE:
            return osd_map['crush']['buckets']
        elif object_type == CRUSH_TYPE:
            return osd_map['crush']['types']
        else:
            raise NotImplementedError(object_type)

    def _dump_request(self, request):
        """UserRequest to JSON-serializable form

        """
        return {
            'id': request.id,
            'state': request.state,
            'error': request.error,
            'error_message': request.error_message,
            'status': request.status,
            'headline': request.headline,
            'requested_at': request.requested_at.isoformat(),
            'completed_at':
            request.completed_at.isoformat()
            if request.completed_at else None
        }

    def get_request(self, request_id):
        """Get a JSON representation of a UserRequest

        """
        try:
            return self._dump_request(
                self._manager.requests.get_by_id(request_id))
        except KeyError:
            raise NotFound('request', request_id)

    def cancel_request(self, request_id):
        try:
            self._manager.requests.cancel(request_id)
            return self.get_request(request_id)
        except KeyError:
            raise NotFound('request', request_id)

    def list_requests(self, filter_args):
        state = filter_args.get('state', None)
        fsid = filter_args.get('fsid', None)
        requests = self._manager.requests.get_all()
        return sorted([self._dump_request(r)
                       for r in requests
                       if (
            state is None or r.state == state
        ) and (fsid is None or r.fsid == fsid)],
            lambda a, b: cmp(b['requested_at'], a['requested_at']))

    def server_get(self, fqdn):
        return self._manager.servers.dump(self._server_resolve(fqdn))

    def server_list(self):
        return [
            self._manager.servers.dump(
                s
            ) for s in self._manager.servers.get_all()
        ]

    def server_get_cluster(self, fqdn, fsid):
        return self._manager.servers.dump_cluster(
            self._server_resolve(fqdn), self._fs_resolve(fsid)
        )

    def server_list_cluster(self, fsid):
        return [
            self._manager.servers.dump_cluster(s, self._manager.clusters[fsid])
            for s in self._manager.servers.get_all_cluster(fsid)
        ]

    def server_by_service(self, services):
        """Return a list of 2-tuples mapping of service ID to server FQDN

        Note that we would rather return a dict but tuple dict keys are

        awkward to serialize

        """
        result = self._manager.servers.list_by_service(
            [ServiceId(*s) for s in services])
        return result

    def server_delete(self, fqdn):
        return self._manager.servers.delete(fqdn)

    def status_by_service(self, services):
        result = self._manager.servers.get_services(
            [ServiceId(*s) for s in services])
        return [
            ({'running': ss.running, 'server': ss.server_state.fqdn,
              'status': ss.status} if ss else None
             )
            for ss in result
        ]


class EtcdRPC(object):

    def __init__(self, methods):
        self._methods = self._filter_methods(EtcdRPC, self, methods)
        etcd_kwargs = {'port': int(config.get("bridge", "etcd_port")),
                       'host': config.get("bridge", "etcd_connection")}

        self.client = etcd.Client(**etcd_kwargs)
        self.bridge_id = str(uuid.uuid4())

    @staticmethod
    def _filter_methods(cls, self, methods):
        if hasattr(methods, '__getitem__'):
            return methods
        server_methods = set(getattr(self, k) for k in dir(cls) if not
                             k.startswith('_'))
        return dict((k, getattr(methods, k))
                    for k in dir(methods)
                    if callable(
            getattr(methods, k)
        ) and not k.startswith('_') and getattr(
                        methods, k) not in server_methods
        )

    def __call__(self, method, kwargs=None, *args):
        if method not in self._methods:
            raise NameError(method)
        return self._methods[method](*args, **kwargs)

    def _acceptor(self):
        while True:
            raw_jobs = self.client.read("/rawops/jobs")
            jobs = sorted(json.loads(raw_jobs.value),
                          key=lambda k: int(k['updated']))
            # Pick up the oldest job that is not locked by any other bridge
            try:
                for job in jobs:

                    if not job['locked_by']:
                        # First lock the job

                        log.info("%s found new job_%s" %
                                 (self.__class__.__name__, job['job_id']))
                        log.debug(job['msg'])
                        job['locked_by'] = self.bridge_id
                        job['status'] = "in-progress"
                        job['updated'] = int(time.time())
                        raw_jobs.value = json.dumps(jobs)
                        self.client.write("/rawops/jobs", raw_jobs.value)
                        log.info("%s Running new job_%s" %
                                 (self.__class__.__name__, job['job_id']))
                        self.__call__(job['msg']['func'],
                                      kwargs=job['msg']['kwargs'])
                        job['updated'] = int(time.time())
                        job['status'] = "complete"
                        raw_jobs.value = json.dumps(jobs)
                        self.client.write("/rawops/jobs", raw_jobs.value)
                        log.info("%s Completed job_%s" %
                                 (self.__class__.__name__, job['job_id']))

                        break
            except Exception as ex:
                log.error(ex)
            gevent.sleep(1)

    def run(self):
        self._acceptor()

    def stop(self):
        pass


class EtcdThread(gevent.greenlet.Greenlet):
    """Present a ZeroRPC API for users

    to request state changes.

    """

    # In case server.run throws an exception, prevent
    # really aggressive spinning
    EXCEPTION_BACKOFF = 5

    def __init__(self, manager):
        super(EtcdThread, self).__init__()
        self._manager = manager
        self._complete = gevent.event.Event()
        self._server = EtcdRPC(RpcInterface(manager))

    def stop(self):
        log.info("%s stopping" % self.__class__.__name__)

        self._complete.set()
        if self._server:
            self._server.stop()

    def _run(self):

        while not self._complete.is_set():
            try:
                log.info("%s run..." % self.__class__.__name__)
                self._server.run()
            except Exception:
                log.error(traceback.format_exc())
                self._complete.wait(self.EXCEPTION_BACKOFF)

        log.info("%s complete..." % self.__class__.__name__)
