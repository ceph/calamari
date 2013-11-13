

def enable_gevent():
    # We are using gevent because:
    #
    # - ZeroRPC requires it
    # - It is nice and efficient anyway.

    from gevent.monkey import patch_all
    patch_all()
    import zmq.green
    import salt.utils.event
    salt.utils.event.zmq = zmq.green

enable_gevent()

import datetime
import json
import logging
import traceback
import dateutil
from dateutil.tz import tzlocal
import threading
import threading2
import salt
import salt.utils.event
import salt.client
from salt.client import condition_kwarg
import zerorpc
import zmq

from cthulhu import persistence

log = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
log.addHandler(handler)
handler = logging.FileHandler("{0}.log".format(__name__))
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
log.addHandler(handler)
log.setLevel(logging.DEBUG)
log.setLevel(logging.DEBUG)


CTHULHU_RPC_URL = 'tcp://127.0.0.1:5050'
REST_ADDRESS = ('0.0.0.0', 8080)
SALT_CONFIG_PATH = './salt/etc/salt/master'
SALT_RUN_PATH = './salt/var/run/salt/master'
# FIXME: this should be a function of the ceph.heartbeat schedule period which
# we should query from the salt pillar
FAVORITE_TIMEOUT_S = 60


class ClusterUnavailable(Exception):
    pass


class PublishError(Exception):
    pass


class SyncObject(object):
    """
    An object from a Ceph cluster that we are maintaining
    a copy of on the Calamari server.
    """
    def __init__(self, version, data):
        self.version = version
        self.data = data


class OsdMap(SyncObject):
    str = 'osd_map'


class OsdTree(SyncObject):
    str = 'osd_tree'


class MdsMap(SyncObject):
    str = 'mds_map'


class MonMap(SyncObject):
    str = 'mon_map'


class MonStatus(SyncObject):
    str = 'mon_status'


class PgBrief(SyncObject):
    str = 'pg_brief'


class Health(SyncObject):
    str = 'health'

OSD = 'osd'
CEPH_OBJECT_TYPES = [OSD]

SYNC_OBJECT_TYPES = [MdsMap, OsdMap, OsdTree, MonMap, MonStatus, PgBrief, Health]

str_to_type = dict((t.str, t) for t in SYNC_OBJECT_TYPES)


class SyncObjects(object):
    """
    A collection of versioned objects, keyed by their class (which
    must be a SyncObject subclass)
    """
    def __init__(self):
        self._objects = dict([(t, None) for t in SYNC_OBJECT_TYPES])

    def set_map(self, typ, version, map_data):
        self._objects[typ] = typ(version, map_data)

    def get_version(self, typ):
        return self._objects[typ].version if self._objects[typ] else None

    def get(self, typ):
        return self._objects[typ]

    @property
    def version(self):
        return tuple(self.get_version(t) for t in SYNC_OBJECT_TYPES)

    def __repr__(self):
        return "<%s>: %s" % (self.__class__.__name__, self.version)


class UserRequest(object):
    """
    A request acts on one or more Ceph-managed objects, i.e.
    mon, mds, osd, pg.

    XXX Should requests include predicition of their side effects,
    e.g. an osd operation will have side effects on PGs?

    XXX Where should we generate severities/warnings for potential
    events?  e.g. setting one OSD to down may need no confirmation,
    setting more than one might be a warning, setting more than N when
    replication is at level N might be a severe warning about making
    some PGs unavailable?
    """

    def __init__(self, minion_id, cluster_name, commands):
        # A request is always initiated at a known epoch, the maps
        # at this epoch were the ones used to decide whether this
        # job was valid.

        self.requested_at = datetime.datetime.now(tzlocal())

        self._minion_id = minion_id
        self._cluster_name = cluster_name
        self._commands = commands

        self._jid = None

        self.is_complete = False
        self.result = False

    @property
    def submitted(self):
        return self._jid is not None

    @property
    def request_id(self):
        return self._jid

    def submit(self):
        assert not self.submitted

        # We are out of date: request an up to date copy
        client = salt.client.LocalClient(SALT_CONFIG_PATH)
        pub_data = client.run_job(self._minion_id, 'ceph.rados_commands', [self._cluster_name, self._commands])
        if not pub_data:
            # FIXME: LocalClient uses 'print' to record the
            # details of what went wrong :-(
            raise PublishError("Failed to publish job")
        self._jid = pub_data['jid']

    def complete(self, result):
        self.is_complete = True
        self.result = result
        log.info("Request %s completed with result=%s" % (self.request_id, self.result))


class RpcInterface(object):
    def __init__(self, manager):
        self._manager = manager

    def _fs_resolve(self, fs_id):
        return self._manager.monitors[fs_id]

    def _osd_resolve(self, fs_id, osd_id):
        cluster = self._fs_resolve(fs_id)

        osdmap = cluster._sync_objects.get(OsdMap)
        if osdmap is None:
            raise RuntimeError("No OSD map for FSID %s" % fs_id)

        found_osd = None
        for osd in osdmap.data['osds']:
            if osd['osd'] == osd_id:
                found_osd = osd
        if found_osd is None:
            raise RuntimeError("Bad OSD ID %s" % osd_id)

    def osd_modify(self, fs_id, osd_id, attributes):
        cluster = self._fs_resolve(fs_id)
        # Run a resolve to throw exception if it's unknown
        self._osd_resolve(fs_id, osd_id)
        if not 'id' in attributes:
            attributes['id'] = osd_id

        req = cluster.request_change(OSD, [attributes])
        return {'id': req.request_id}

    def osd_get(self, fs_id, osd_id):
        return self._osd_resolve(fs_id, osd_id)

    def osd_list(self, fs_id):
        cluster = self._fs_resolve(fs_id)
        return cluster._sync_objects.get(OsdMap).data

    def hello(self, name):
        return "hello %s" % name


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


class RequestCollection(dict):
    def __init__(self):
        super(RequestCollection, self).__init__()
        self._shlock = threading2.SHLock()

    def put(self, request):
        assert request.submitted

        self._shlock.acquire(shared=False)
        try:
            self[request.request_id] = request
        finally:
            self._shlock.release()

    def get_one(self, request_id):
        self._shlock.acquire(shared=True)
        try:
            return self[request_id]
        finally:
            self._shlock.release()

    def get_all(self):
        self._shlock.acquire(shared=True)
        try:
            return self.values()
        finally:
            self._shlock.release()


class DiscoveryThread(threading.Thread):
    def __init__(self, manager):
        super(DiscoveryThread, self).__init__()

        self._manager = manager
        self._complete = threading.Event()

    def stop(self):
        self._complete.set()

    def run(self):
        log.info("%s running" % self.__class__.__name__)
        event = salt.utils.event.MasterEvent(SALT_RUN_PATH)
        event.subscribe("ceph/heartbeat/")

        while not self._complete.is_set():
            data = event.get_event()
            if data is not None:
                try:
                    if 'tag' in data and data['tag'].startswith("ceph/heartbeat/"):
                        cluster_data = data['data']
                        if not cluster_data['fsid'] in self._manager.monitors:
                            self._manager.on_discovery(data['id'], cluster_data)
                        else:
                            log.debug("%s: heartbeat from existing cluster %s" % (
                                self.__class__.__name__, cluster_data['fsid']))
                    else:
                        # This does not concern us, ignore it
                        #log.debug("DiscoveryThread ignoring: %s" % data)
                        pass
                except:
                    log.error("Exception handling message: %s" % traceback.format_exc())
                    log.debug("Message content: %s" % data)

        log.info("%s complete" % self.__class__.__name__)


class Manager(object):
    """
    Manage a collection of ClusterMonitors.

    Subscribe to ceph/heartbeat events, and create a ClusterMonitor
    for any FSID we haven't seen before.
    """

    def __init__(self):
        self._complete = threading.Event()

        self._request_thread = RpcThread(self)
        self._discovery_thread = DiscoveryThread(self)
        self._notification_thread = NotificationThread()

        # FSID to ClusterMonitor
        self.monitors = {}

    def stop(self):
        log.info("%s stopping" % self.__class__.__name__)
        for monitor in self.monitors.values():
            monitor.stop()
        self._request_thread.stop()
        self._discovery_thread.stop()
        self._notification_thread.stop()

    def start(self):
        log.info("%s starting" % self.__class__.__name__)
        self._request_thread.start()
        self._discovery_thread.start()
        self._notification_thread.start()

    def join(self):
        log.info("%s joining" % self.__class__.__name__)
        self._request_thread.join()
        self._discovery_thread.join()
        self._notification_thread.join()
        for monitor in self.monitors.values():
            monitor.join()

    def on_discovery(self, minion_id, heartbeat_data):
        log.info("on_discovery: {0}/{1}".format(minion_id, heartbeat_data['fsid']))
        cluster_monitor = ClusterMonitor(heartbeat_data['fsid'], heartbeat_data['name'], self._notification_thread)
        self.monitors[heartbeat_data['fsid']] = cluster_monitor

        persistence.get_or_create(
            heartbeat_data['name']
        )

        # Run before passing on the heartbeat, because otherwise the
        # syncs resulting from the heartbeat might not be received
        # by the monitor.
        cluster_monitor.start()
        cluster_monitor.on_heartbeat(minion_id, heartbeat_data)


class NotificationThread(threading.Thread):
    """
    Responsible for:
     - Listening for Websockets clients connecting, and subscribing them
       to the ceph: topics
     - Publishing messages to Websockets topics on behalf of other
       python code.
    """
    def __init__(self):
        super(NotificationThread, self).__init__()
        self._complete = threading.Event()
        self._pub = None
        self._ready = threading.Event()

    def stop(self):
        self._complete.set()

    def publish(self, topic, message):
        self._ready.wait()
        self._pub.send(b'publish', zmq.SNDMORE)
        self._pub.send(topic, zmq.SNDMORE)
        self._pub.send(json.dumps(message))

    def run(self):
        ctx = zmq.Context(1)
        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://172.16.79.128:7002')
        sub.setsockopt(zmq.SUBSCRIBE, b"")
        self._pub = ctx.socket(zmq.PUB)
        self._pub.connect('tcp://172.16.79.128:7003')
        self._ready.set()
        while not self._complete.is_set():
            try:
                parts = sub.recv_multipart(flags=zmq.NOBLOCK)
            except zmq.ZMQError:
                self._complete.wait(timeout=1)
                continue

            if parts[1] == b'connect':
                self._pub.send(b'subscribe', zmq.SNDMORE)
                self._pub.send(parts[0], zmq.SNDMORE)
                self._pub.send(b'ceph:completion')

                self._pub.send(b'subscribe', zmq.SNDMORE)
                self._pub.send(parts[0], zmq.SNDMORE)
                self._pub.send(b'ceph:sync')


class ClusterMonitor(threading.Thread):
    """
    Remote management of a Ceph cluster.

    Consumes cluster map logs from the mon cluster, maintains
    a record of which user requests are ongoing, and uses this
    combined knowledge to mediate user requests to change the state of the
    system.

    This class spawns two threads, one to listen to salt events and
    another to listen to user requests.
    """
    def __init__(self, fsid, cluster_name, notifier):
        super(ClusterMonitor, self).__init__()

        # Which mon we are currently using for running requests,
        # identified by minion ID
        self._favorite_mon = None

        self._fsid = fsid
        self._name = cluster_name

        self._last_heartbeat = {}

        self._requests = RequestCollection()

        self._complete = threading.Event()

        self._sync_objects = SyncObjects()

        ctx = zmq.Context(1)
        pub = ctx.socket(zmq.PUB)
        pub.connect('tcp://127.0.0.1:7003')
        self._notification_socket = pub

        self._notifier = notifier

    def run(self):
        event = salt.utils.event.MasterEvent(SALT_RUN_PATH)

        while not self._complete.is_set():
            data = event.get_event()
            if data is not None:
                try:
                    if 'tag' in data and data['tag'].startswith("ceph/heartbeat/{0}".format(self._fsid)):
                        # A ceph.heartbeat beacon
                        self.on_heartbeat(data['id'], data['data'])
                    elif 'fun' in data and data['fun'] == 'ceph.get_cluster_object' and 'return' in data:
                        # A ceph.get_cluster_object response
                        # FIXME: ordering: should be tracking ongoing jids for each type of object
                        # we might have a sync out for, and
                        # FIXME: filtering: chop these down to only the jobs for this cluster, ideally
                        # I would like to prefix my cluster ID to JIDs
                        if not data['success']:
                            log.error("on_sync_object: failure from %s: %s" % (data['id'], data['return']))
                            continue
                        self.on_sync_object(data['id'], data['return'])
                    elif 'fun' in data and data['fun'] == 'ceph.rados_commands' and 'return' in data:
                        # A ceph.rados_commands response
                        self.on_completion(data)
                    else:
                        # This does not concern us, ignore it
                        pass
                except:
                    log.error("Exception handling message: %s" % traceback.format_exc())
                    log.debug("Message content: %s" % data)

        log.info("%s complete" % self.__class__.__name__)

    def stop(self):
        log.info("%s stopping" % self.__class__.__name__)
        self._complete.set()

    def is_favorite(self, minion_id):
        """
        Check if this minion is the one which we are currently treating
        as the primary source of updates, and promote it to be the
        favourite if the favourite has not sent a heartbeat since
        FAVORITE_TIMEOUT_S.

        :return True if this minion was the favorite or has just been
                promoted.
        """
        now = datetime.datetime.now(tz=dateutil.tz.tzlocal())
        self._last_heartbeat[minion_id] = now

        if self._favorite_mon is None:
            log.debug("%s is my new favourite" % minion_id)
            self.set_favorite(minion_id)
            return True
        elif minion_id != self._favorite_mon:
            # Consider whether this minion should become my new favourite: has it been
            # too long since my current favourite reported in?
            time_since = now - self._last_heartbeat[self._favorite_mon]
            if time_since > datetime.timedelta(seconds=FAVORITE_TIMEOUT_S):
                log.debug("My old favourite, %s, has not sent a heartbeat for %s: %s is my new favourite" % (
                    self._favorite_mon, time_since, minion_id
                ))
                self.set_favorite(minion_id)

        return minion_id == self._favorite_mon

    def on_heartbeat(self, minion_id, cluster_data):
        """
        Handle a ceph.heartbeat from a minion.

        Heartbeats come from all servers, but we're mostly interested in those
        which come from a mon (and therefore have the 'clusters' attribute populated)
        as these tells us whether there are any new versions of cluster maps
        for us to fetch.
        """

        if not self.is_favorite(minion_id):
            log.debug('Ignoring cluster data from %s, it is not my favourite (%s)' % (minion_id, self._favorite_mon))
            return

        log.debug('Checking for version increments in heartbeat from %s' % minion_id)

        for sync_type in SYNC_OBJECT_TYPES:
            old_version = self._sync_objects.get_version(sync_type)
            new_version = cluster_data['versions'][sync_type.str]
            # FIXME: for versions (not hashes) check for greater than, not just inequality
            if new_version != old_version:
                log.info("Advanced version %s/%s %s->%s" % (self._fsid, sync_type.str, old_version, new_version))

                # We are out of date: request an up to date copy
                client = salt.client.LocalClient(SALT_CONFIG_PATH)
                client.run_job(minion_id, 'ceph.get_cluster_object', condition_kwarg([], {
                    'cluster_name': cluster_data['name'],
                    'sync_type': sync_type.str,
                    'since': old_version
                }))

        persistence.heartbeat()

    def on_sync_object(self, minion_id, data):
        if minion_id != self._favorite_mon:
            log.debug("Ignoring map from %s, it is not my favourite (%s)" % (minion_id, self._favorite_mon))

        fsid = data['fsid']

        sync_type = str_to_type[data['type']]

        if data['version'] != self._sync_objects.get_version(sync_type):
            log.info("Received new copy of %s/%s: %s" % (fsid, sync_type.str, data['version']))
            self._notifier.publish('ceph:sync', {
                'type': data['type'],
                'version': data['version'],
                'data': data['data']
            })

            self._sync_objects.set_map(sync_type, data['version'], data['data'])

            # FIXME: should push persistence ops to a queue instead of doing it in the here and now
            if sync_type in [OsdMap, MdsMap, MonStatus, PgBrief]:
                if None not in map(lambda t: self._sync_objects.get_version(t), [OsdMap, MdsMap, MonStatus, PgBrief]):
                    persistence.populate_counters(
                        self._sync_objects.get(OsdMap).data,
                        self._sync_objects.get(MdsMap).data,
                        self._sync_objects.get(MonStatus).data,
                        self._sync_objects.get(PgBrief).data
                    )

            if sync_type in [OsdMap, PgBrief, OsdTree]:
                if None not in map(lambda t: self._sync_objects.get_version(t), [OsdMap, OsdTree, PgBrief]):
                    persistence.populate_osds_and_pgs(
                        self._sync_objects.get(OsdMap).data,
                        self._sync_objects.get(OsdTree).data,
                        self._sync_objects.get(PgBrief).data
                    )

            if sync_type is Health:
                persistence.populate_health(data['data'])

    def on_completion(self, data):
        jid = data['jid']
        result = data['return']
        log.debug("on_completion: jid=%s" % jid)

        request = self._requests.get_one(jid)
        request.complete(result)

        self._notifier.publish('ceph:completion', {'jid': jid})

    def set_favorite(self, minion_id):
        self._favorite_mon = minion_id
        # TODO: for use when we have lost contact
        # with the existing favorite: if we had any
        # outstanding jobs which were using it, then
        # synthesize failures for them.

    def request_change(self, obj_type, patches):
        """

        This function requires a read lock on the cluster map.
        This function requires a read lock and briefly a write lock on the request collection.

        :param obj_type: OSD, MDS, MON or PG
        :param patches: List of dicts, each dict must have at least 'id' attribute.
        """
        log.debug("Request_change: %s/%s" % (obj_type, patches))
        if self._favorite_mon is None:
            log.error("request_change: don't have a favourite to run on")
            raise ClusterUnavailable()

        if obj_type not in CEPH_OBJECT_TYPES:
            raise ValueError("{0} is not one of {1}".format(obj_type, CEPH_OBJECT_TYPES))

        # TODO Acquire cluster map read lock and request collection read lock
        # TODO Validate the requested change against the cluster map and ongoing requests

        # TODO: Use some per-object-type logic to work out what commands are
        # needed to 'make it so' for the patches passed in.
        commands = []
        if obj_type == OSD:
            for p in patches:
                if p['in'] == 0:
                    commands.append(('osd out', {'ids': [p['id'].__str__()]}))
                else:
                    commands.append(('osd in', {'ids': [p['id'].__str__()]}))

        # TODO: provide some per-object-type ability to emit human readable descriptions
        # of what we are doing.

        # TOOD: provide some machine-readable indication of which objects are affected
        # by a particular request.
        # Perhaps subclass Request for each type of object, and have that subclass provide
        # both the patches->commands mapping and the human readable and machine readable
        # descriptions of it?
        req = UserRequest(self._favorite_mon, self._name, commands)

        try:
            req.submit()
        except ClusterUnavailable:
            # TODO: Handle mon going away: interrogate salt to find a connected mon
            # and make that the new favourite.
            raise

        self._requests.put(req)

        return req


def main():
    m = Manager()
    m.start()

    try:
        complete = threading.Event()
        while not complete.is_set():
            complete.wait(timeout=1)
    except KeyboardInterrupt:
        # TODO signal handling
        log.info("KeyboardInterrupt: stopping")
        m.stop()
        m.join()
