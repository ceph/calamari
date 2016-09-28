import datetime
import time

import gevent.event
import gevent.greenlet
from pytz import utc

from ceph_bridge import ceph
from ceph_bridge import config
from ceph_bridge.gevent_util import nosleep
from ceph_bridge.gevent_util import nosleep_mgr
from ceph_bridge import log
from ceph_bridge.manager.crush_node_request_factory \
    import CrushNodeRequestFactory
from ceph_bridge.manager.crush_request_factory \
    import CrushRequestFactory
from ceph_bridge.manager.osd_request_factory import OsdRequestFactory
from ceph_bridge.manager.pool_request_factory import PoolRequestFactory
from ceph_bridge.types import CRUSH_MAP
from ceph_bridge.types import CRUSH_NODE
from ceph_bridge.types import MdsMap
from ceph_bridge.types import MonMap
from ceph_bridge.types import OSD
from ceph_bridge.types import OsdMap
from ceph_bridge.types import POOL
from ceph_bridge.types import SYNC_OBJECT_STR_TYPE
from ceph_bridge.types import SYNC_OBJECT_TYPES
from ceph_bridge.util import now

FAVORITE_TIMEOUT_FACTOR = int(config.get('bridge', 'favorite_timeout_factor'))

LOG = log.g


class ClusterUnavailable(Exception):
    pass


class SyncObjects(object):
    """A collection of versioned objects, keyed by their class (which

    must be a SyncObject subclass).

    The objects are immutable, so it is safe to hand out references: new

    versions are new objects.

    """

    # Note that this *isn't* an enforced timeout on fetches, rather it is
    # the time after which we will start re-requesting maps on the assumption
    # that a previous fetch is MIA.
    FETCH_TIMEOUT = datetime.timedelta(seconds=10)

    def __init__(self, cluster_name):
        self._objects = dict([(t, t(None, None)) for t in SYNC_OBJECT_TYPES])
        self._cluster_name = cluster_name

        # When we issued a fetch() for this type, or None if no fetch
        # is underway
        self._fetching_at = dict([(t, None) for t in SYNC_OBJECT_TYPES])
        # The latest version we have heard about (not the latest we have
        # in our map)
        self._known_versions = dict([(t, None) for t in SYNC_OBJECT_TYPES])

    def set_map(self, typ, version, map_data):
        so = self._objects[typ] = typ(version, map_data)
        return so

    def get_version(self, typ):
        return self._objects[typ].version if self._objects[typ] else None

    def get_data(self, typ):
        return self._objects[typ].data if self._objects[typ] else None

    def get(self, typ):
        return self._objects[typ]

    def on_version(self, sync_type, new_version):
        """Notify me that a particular version of a particular map exists.

        I may choose to initiate RPC to retrieve the map

        """
        log.debug(
            "SyncObjects.on_version %s/%s" % (sync_type.str, new_version)
        )
        old_version = self.get_version(sync_type)
        if sync_type.cmp(new_version, old_version) > 0:
            known_version = self._known_versions[sync_type]
            if sync_type.cmp(new_version, known_version) > 0:
                # We are out of date: request an up to date copy
                log.info("Advanced known version %s/%s %s->%s" % (
                    self._cluster_name,
                    sync_type.str,
                    known_version,
                    new_version)
                )
                self._known_versions[sync_type] = new_version
            else:
                log.info(
                    "on_version: %s is newer than %s" % (
                        new_version, old_version
                    )
                )

            # If we already have a request out for this type of map,
            # then consider cancelling it if we've already waited for
            # a while.
            if self._fetching_at[sync_type] is not None:
                if now() - self._fetching_at[sync_type] < self.FETCH_TIMEOUT:
                    log.info("Fetch already underway for %s" % sync_type.str)
                    return
                else:
                    log.warn("Abandoning fetch for %s started at %s" % (
                        sync_type.str, self._fetching_at[sync_type]))

            log.info(
                "on_version: fetching %s/%s , "
                "currently got %s, know %s" % (
                    sync_type, new_version, old_version, known_version
                )
            )
            return self.fetch(sync_type)

    def fetch(self, sync_type):
        log.debug("SyncObjects.fetch: %s" % sync_type)

        self._fetching_at[sync_type] = now()
        # TODO(Rohan) clean up unused 'since' argument
        return ceph.get_cluster_object(self._cluster_name,
                                       sync_type.str, None)

    def on_fetch_complete(self, sync_type, version, data):
        """:return A SyncObject if this version was new to us, else None

        """
        log.debug(
            "SyncObjects.on_fetch_complete %s/%s" % (
                sync_type.str, version)
        )
        self._fetching_at[sync_type] = None

        # A fetch might give us a newer version than we knew we had asked for
        if sync_type.cmp(version, self._known_versions[sync_type]) > 0:
            self._known_versions[sync_type] = version

        # Don't store this if we already got something newer
        if sync_type.cmp(version, self.get_version(sync_type)) <= 0:
            log.warn(
                "Ignoring outdated"
                " update %s/%s" % (sync_type.str, version)
            )
            new_object = None
        else:
            log.info("Got new version %s/%s" % (sync_type.str, version))
            new_object = self.set_map(sync_type, version, data)

        # This might not be the latest: if it's not, send out another fetch
        # right away
        # if sync_type.cmp(self._known_versions[sync_type], version) > 0:
        #    self.fetch(sync_type)

        return new_object


class ClusterMonitor(gevent.greenlet.Greenlet):
    """Remote management of a Ceph cluster.

    Consumes cluster map logs from the mon cluster, maintains

    a record of which user requests are ongoing, and uses this

    combined knowledge to mediate user requests to change the state of the

    system.

    This class spawns two threads, one to listen to salt events and

    another to listen to user requests.

    """

    def __init__(self, fsid, cluster_name, persister, servers, eventer):
        super(ClusterMonitor, self).__init__()

        self.fsid = fsid
        self.name = cluster_name
        self.update_time = datetime.datetime.utcnow().replace(tzinfo=utc)

        self._persister = persister
        self._servers = servers
        self._eventer = eventer

        # Which mon we are currently using for running requests,
        # identified by minion ID
        self._favorite_mon = None
        self._last_heartbeat = {}

        self._complete = gevent.event.Event()
        self.done = gevent.event.Event()

        self._sync_objects = SyncObjects(self.name)

        self._request_factories = {
            CRUSH_MAP: CrushRequestFactory,
            CRUSH_NODE: CrushNodeRequestFactory,
            OSD: OsdRequestFactory,
            POOL: PoolRequestFactory
        }

        self._ready = gevent.event.Event()

    def ready(self):
        """Block until the ClusterMonitor is ready to receive salt events

        """
        self._ready.wait()

    def stop(self):
        log.info("%s stopping" % self.__class__.__name__)
        self._complete.set()

    @nosleep
    def get_sync_object_data(self, object_type):
        """:param object_type: A SyncObject subclass

        :returns: a json-serializable object

        """
        return self._sync_objects.get_data(object_type)

    @nosleep
    def get_sync_object(self, object_type):
        """:param object_type: A SyncObject subclass

        :returns: a SyncObject instance

        """
        return self._sync_objects.get(object_type)

    def _run(self):

        self._ready.set()
        log.debug("ClusterMonitor._run: ready")

        while not self._complete.is_set():

            data = ceph.heartbeat(heartbeat_type="cluster", fsid=self.fsid)

            if data is not None:
                for tag, c_data in data.iteritems():
                    log.debug(
                        "ClusterMonitor._run.ev:"
                        " %s/tag=%s" % (
                            c_data['id'] if 'id' in c_data else None, tag)
                    )

                try:
                    if tag.startswith("ceph/cluster/{0}".format(self.fsid)):
                        # A ceph.heartbeat beacon
                        self.on_heartbeat(c_data['id'], c_data)
                    else:
                        # This does not concern us, ignore it
                        pass
                except Exception:
                    # Because this is our main event handling loop, swallow
                    # exceptions instead of letting them end the world.
                    log.exception(
                        "Exception handling message with tag %s" % tag)
                    log.debug("Message content: %s" % data)
            gevent.sleep(4)

        log.info("%s complete" % self.__class__.__name__)
        self.done.set()

    @nosleep
    def on_version(self, sync_type, version):
        self._sync_objects.on_version(sync_type, version)

    @nosleep
    def on_heartbeat(self, fqdn, cluster_data):
        """Handle a ceph.heartbeat from a minion.

        Heartbeats come from all servers, but we're mostly interested in those

        which come from a mon (and therefore have the 'clusters' attribute

        populated) as these tells us whether there are any new versions of

        cluster maps for us to fetch.

        """

        self.update_time = datetime.datetime.utcnow().replace(tzinfo=utc)

        log.debug('Checking for version increments in heartbeat')
        for sync_type in SYNC_OBJECT_TYPES:
            data = self._sync_objects.on_version(
                sync_type, cluster_data['versions'][sync_type.str]
            )
            if data:
                self.on_sync_object(data)

    def inject_sync_object(self, sync_type, version, data):
        sync_type = SYNC_OBJECT_STR_TYPE[sync_type]
        old_object = self._sync_objects.get(sync_type)
        new_object = self._sync_objects.on_fetch_complete(
            sync_type, version, data
        )

        if new_object:
            # The ServerMonitor is interested in cluster maps
            if sync_type == OsdMap:
                self._servers.on_osd_map(data)
            elif sync_type == MonMap:
                self._servers.on_mon_map(data)
            elif sync_type == MdsMap:
                self._servers.on_mds_map(self.fsid, data)

            self._eventer.on_sync_object(
                self.fsid, sync_type, new_object, old_object
            )

        return new_object

    @nosleep
    def on_sync_object(self, data):

        assert data['fsid'] == self.fsid

        sync_object = data['data']

        sync_type = SYNC_OBJECT_STR_TYPE[data['type']]
        new_object = self.inject_sync_object(
            data['type'], data['version'], sync_object
        )
        if new_object:
            self._persister.update_sync_object(
                str(time.time()),
                self.fsid,
                self.name,
                sync_type.str,
                new_object.version if isinstance(
                    new_object.version, int
                ) else None,
                now(), sync_object)
        else:
            log.warn(
                "ClusterMonitor.on_sync_object: stale object"
                " received for %s" % data['type']
            )

    def _request(self, method, obj_type, *args, **kwargs):
        """Create and submit UserRequest for an apply, create, update or delete.

        """

        # nosleep during preparation phase (may touch
        # ClusterMonitor/ServerMonitor state)
        request = None
        with nosleep_mgr():
            request_factory = self.get_request_factory(obj_type)

            request = getattr(request_factory, method)(*args, **kwargs)

        response = request.submit()
        if request:
            return {
                'request_id': request.id,
                'response': response
            }
        else:
            return None

    def request_delete(self, obj_type, obj_id):
        return self._request('delete', obj_type, obj_id)

    def request_create(self, obj_type, attributes):
        return self._request('create', obj_type, attributes)

    def request_update(self, command, obj_type, obj_id, attributes):
        return self._request(command, obj_type, obj_id, attributes)

    def request_apply(self, obj_type, obj_id, command):
        return self._request(command, obj_type, obj_id)

    def get_valid_commands(self, object_type, obj_ids):
        return self.get_request_factory(
            object_type).get_valid_commands(obj_ids)

    def get_request_factory(self, object_type):
        try:
            return self._request_factories[object_type](self)
        except KeyError:
            raise ValueError(
                "{0} is not one of {1}".format(
                    object_type, self._request_factories.keys()
                )
            )
