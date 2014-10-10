import traceback
import gevent.event

try:
    import zerorpc
except ImportError:
    zerorpc = None

from calamari_common.salt_wrapper import Key, master_config, LocalClient
from cthulhu.manager import config
from cthulhu.log import log
from calamari_common.types import OsdMap, SYNC_OBJECT_STR_TYPE, OSD, OSD_MAP, POOL, CLUSTER, CRUSH_NODE, CRUSH_MAP, CRUSH_RULE, ServiceId,\
    NotFound, SERVER
from cthulhu.manager.user_request import SaltRequest


class RpcInterface(object):
    def __init__(self, manager):
        self._manager = manager

    def __getattribute__(self, item):
        """
        Wrap functions with logging
        """
        if item.startswith('_'):
            return object.__getattribute__(self, item)
        else:
            attr = object.__getattribute__(self, item)
            if callable(attr):
                def wrap(*args, **kwargs):
                    log.debug("RpcInterface >> %s(%s, %s)" % (item, args, kwargs))
                    try:
                        rc = attr(*args, **kwargs)
                        log.debug("RpcInterface << %s" % item)
                    except:
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
        """
        Returns a dict, or None if not found
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
        """
        Get one of the objects that ClusterMonitor keeps a copy of from the mon, such
        as the cluster maps.

        :param fs_id: The fsid of a cluster
        :param object_type: String, one of SYNC_OBJECT_TYPES
        :param path: List, optional, a path within the object to return instead of the whole thing

        :return: the requested data, or None if it was not found (including if any element of ``path``
                 was not found)
        """

        if path:
            obj = self._fs_resolve(fs_id).get_sync_object(SYNC_OBJECT_STR_TYPE[object_type])
            try:
                for part in path:
                    if isinstance(obj, dict):
                        obj = obj[part]
                    else:
                        obj = getattr(obj, part)
            except (AttributeError, KeyError) as e:
                log.exception("Exception %s traversing %s: obj=%s" % (e, path, obj))
                raise NotFound(object_type, path)
            return obj
        else:
            return self._fs_resolve(fs_id).get_sync_object_data(SYNC_OBJECT_STR_TYPE[object_type])

    def update(self, fs_id, object_type, object_id, attributes):
        """
        Modify an object in a cluster.
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

            return cluster.request_update('update', POOL, object_id, attributes)
        elif object_type == OSD_MAP:
            return cluster.request_update('update_config', OSD, object_id, attributes)

        elif object_type == CRUSH_MAP:
            return cluster.request_update('update', CRUSH_MAP, object_id, attributes)

        elif object_type == CRUSH_NODE:
            return cluster.request_update('update', CRUSH_NODE, object_id, attributes)

        else:
            raise NotImplementedError(object_type)

    def debug_job(self, minion_id, cmd, args):
        """
        Used in synthetic testing.
        """
        request = SaltRequest(cmd, args)
        self._manager.requests.submit(request, minion_id)
        return {
            'request_id': request.id
        }

    def apply(self, fs_id, object_type, object_id, command):
        """
        Apply commands that do not modify an object in a cluster.
        """
        cluster = self._fs_resolve(fs_id)

        if object_type == OSD:
            # Run a resolve to throw exception if it's unknown
            self._osd_resolve(cluster, object_id)
            return cluster.request_apply(OSD, object_id, command)

        else:
            raise NotImplementedError(object_type)

    def get_valid_commands(self, fs_id, object_type, object_ids):
        """
        Determine what commands can be run on OSD object_ids
        """
        if object_type != OSD:
            raise NotImplementedError(object_type)

        cluster = self._fs_resolve(fs_id)
        try:
            valid_commands = cluster.get_valid_commands(object_type, object_ids)
        except KeyError as e:
            raise NotFound(object_type, str(e))

        return valid_commands

    def create(self, fs_id, object_type, attributes):
        """
        Create a new object in a cluster
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
        """
        Get one object from a particular cluster.
        """

        cluster = self._fs_resolve(fs_id)
        if object_type == OSD:
            return self._osd_resolve(cluster, object_id)
        elif object_type == POOL:
            return self._pool_resolve(cluster, object_id)
        elif object_type == CRUSH_NODE:
            try:
                crush_node = cluster.get_sync_object(OsdMap).crush_node_by_id[object_id]
            except KeyError:
                raise NotFound(CRUSH_NODE, object_id)
            return crush_node
        else:
            raise NotImplementedError(object_type)

    def list(self, fs_id, object_type, list_filter):
        """
        Get many objects
        """

        cluster = self._fs_resolve(fs_id)
        osd_map = cluster.get_sync_object_data(OsdMap)
        if osd_map is None:
            return []
        if object_type == OSD:
            result = osd_map['osds']
            if 'id__in' in list_filter:
                result = [o for o in result if o['osd'] in list_filter['id__in']]
            if 'pool' in list_filter:
                try:
                    osds_in_pool = cluster.get_sync_object(OsdMap).osds_by_pool[list_filter['pool']]
                except KeyError:
                    raise NotFound("Pool {0} does not exist".format(list_filter['pool']))
                else:
                    result = [o for o in result if o['osd'] in osds_in_pool]

            return result
        elif object_type == POOL:
            return osd_map['pools']
        elif object_type == CRUSH_RULE:
            return osd_map['crush']['rules']
        elif object_type == CRUSH_NODE:
            return osd_map['crush']['buckets']
        else:
            raise NotImplementedError(object_type)

    def _dump_request(self, request):
        """UserRequest to JSON-serializable form"""
        return {
            'id': request.id,
            'state': request.state,
            'error': request.error,
            'error_message': request.error_message,
            'status': request.status,
            'headline': request.headline,
            'requested_at': request.requested_at.isoformat(),
            'completed_at': request.completed_at.isoformat() if request.completed_at else None
        }

    def get_request(self, request_id):
        """
        Get a JSON representation of a UserRequest
        """
        try:
            return self._dump_request(self._manager.requests.get_by_id(request_id))
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
                       if (state is None or r.state == state) and (fsid is None or r.fsid == fsid)],
                      lambda a, b: cmp(b['requested_at'], a['requested_at']))

    def list_server_logs(self, fqdn):
        client = LocalClient(config.get('cthulhu', 'salt_config_path'))
        results = client.cmd(fqdn, "log_tail.list_logs", ["."])
        log.debug('list_server_log result !!! {results}'.format(results=str(results)))
        return results

    def get_server_log(self, fqdn, log_path, lines):
        client = LocalClient(config.get('cthulhu', 'salt_config_path'))
        results = client.cmd(fqdn, "log_tail.tail", [log_path, lines])
        return results

    @property
    def _salt_key(self):
        return Key(master_config(config.get('cthulhu', 'salt_config_path')))

    def minion_status(self, status_filter):
        """
        Return a list of salt minion keys

        :param minion_status: A status, one of acc, pre, rej, all
        """

        # FIXME: I think we're supposed to use salt.wheel.Wheel.master_call
        # for this stuff to call out to the master instead of touching
        # the files directly (need to set up some auth to do that though)

        keys = self._salt_key.list_keys()
        result = []

        key_to_status = {
            'minions_pre': 'pre',
            'minions_rejected': 'rejected',
            'minions': 'accepted'
        }

        for key, status in key_to_status.items():
            for minion in keys[key]:
                if not status_filter or status == status_filter:
                    result.append({
                        'id': minion,
                        'status': status
                    })

        return result

    def minion_accept(self, minion_id):
        """
        :param minion_id: A minion ID, or a glob
        """
        self.minion_get(minion_id)
        return self._salt_key.accept(minion_id)

    def minion_reject(self, minion_id):
        """
        :param minion_id: A minion ID, or a glob
        """
        self.minion_get(minion_id)
        return self._salt_key.reject(minion_id)

    def minion_delete(self, minion_id):
        """
        :param minion_id: A minion ID, or a glob
        """
        self.minion_get(minion_id)
        return self._salt_key.delete_key(minion_id)

    def minion_get(self, minion_id):
        result = self._salt_key.name_match(minion_id, full=True)
        if not result:
            raise NotFound(SERVER, minion_id)

        if 'minions' in result:
            status = "accepted"
        elif "minions_pre" in result:
            status = "pre"
        elif "minions_rejected" in result:
            status = "rejected"
        else:
            raise ValueError(result)

        return {
            'id': minion_id,
            'status': status
        }

    def server_get(self, fqdn):
        return self._manager.servers.dump(self._server_resolve(fqdn))

    def server_list(self):
        return [self._manager.servers.dump(s) for s in self._manager.servers.get_all()]

    def server_get_cluster(self, fqdn, fsid):
        return self._manager.servers.dump_cluster(self._server_resolve(fqdn), self._fs_resolve(fsid))

    def server_list_cluster(self, fsid):
        return [
            self._manager.servers.dump_cluster(s, self._manager.clusters[fsid])
            for s in self._manager.servers.get_all_cluster(fsid)
        ]

    def server_by_service(self, services):
        """
        Return a list of 2-tuples mapping of service ID to server FQDN

        Note that we would rather return a dict but tuple dict keys are awkward to serialize
        """
        result = self._manager.servers.list_by_service([ServiceId(*s) for s in services])
        return result

    def server_delete(self, fqdn):
        return self._manager.servers.delete(fqdn)

    def status_by_service(self, services):
        result = self._manager.servers.get_services([ServiceId(*s) for s in services])
        return [({'running': ss.running, 'server': ss.server_state.fqdn, 'status': ss.status} if ss else None)
                for ss in result]


class RpcThread(gevent.greenlet.Greenlet):
    """
    Present a ZeroRPC API for users
    to request state changes.
    """

    # In case server.run throws an exception, prevent
    # really aggressive spinning
    EXCEPTION_BACKOFF = 5

    def __init__(self, manager):
        super(RpcThread, self).__init__()
        self._manager = manager
        self._complete = gevent.event.Event()
        if zerorpc is None:
            log.error("zerorpc package is missing")
            raise RuntimeError("Cannot run without zerorpc installed!")
        self._server = zerorpc.Server(RpcInterface(manager))
        self._bound = False

    def stop(self):
        log.info("%s stopping" % self.__class__.__name__)

        self._complete.set()
        if self._server:
            self._server.stop()

    def bind(self):
        log.info("%s bind..." % self.__class__.__name__)
        self._server.bind(config.get('cthulhu', 'rpc_url'))
        self._bound = True

    def _run(self):
        assert self._bound

        while not self._complete.is_set():
            try:
                log.info("%s run..." % self.__class__.__name__)
                self._server.run()
            except:
                log.error(traceback.format_exc())
                self._complete.wait(self.EXCEPTION_BACKOFF)

        log.info("%s complete..." % self.__class__.__name__)
