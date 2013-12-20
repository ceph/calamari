import re
import datetime
from dateutil.tz import tzutc

from pytz import utc
import dateutil
import gevent.lock
import gevent

import salt
import salt.utils.event
import salt.client
from salt.client import condition_kwarg
import zmq
from cthulhu.log import log

from cthulhu.manager import derived
from cthulhu.manager.derived import DerivedObjects
from cthulhu.manager.osd_request_factory import OsdRequestFactory
from cthulhu.manager.pool_request_factory import PoolRequestFactory
from cthulhu.manager.types import SYNC_OBJECT_STR_TYPE, SYNC_OBJECT_TYPES, OSD, POOL
from cthulhu.manager.user_request import RequestCollection

from cthulhu.config import SALT_CONFIG_PATH, SALT_RUN_PATH, FAVORITE_TIMEOUT_S


class ClusterUnavailable(Exception):
    pass


class SyncObjects(object):
    """
    A collection of versioned objects, keyed by their class (which
    must be a SyncObject subclass).

    The objects are immutable, so it is safe to hand out references: new
    versions are new objects.
    """

    def __init__(self):
        self._objects = dict([(t, None) for t in SYNC_OBJECT_TYPES])
        self._lock = gevent.lock.RLock()

    def set_map(self, typ, version, map_data):
        with self._lock:
            self._objects[typ] = typ(version, map_data)

    def get_version(self, typ):
        with self._lock:
            return self._objects[typ].version if self._objects[typ] else None

    def get(self, typ):
        with self._lock:
            return self._objects[typ]


class ClusterMonitor(gevent.greenlet.Greenlet):
    """
    Remote management of a Ceph cluster.

    Consumes cluster map logs from the mon cluster, maintains
    a record of which user requests are ongoing, and uses this
    combined knowledge to mediate user requests to change the state of the
    system.

    This class spawns two threads, one to listen to salt events and
    another to listen to user requests.
    """

    def __init__(self, fsid, cluster_name, notifier, persister):
        super(ClusterMonitor, self).__init__()

        self.fsid = fsid
        self.name = cluster_name
        self.update_time = None

        # Which mon we are currently using for running requests,
        # identified by minion ID
        self._favorite_mon = None
        self._last_heartbeat = {}

        self._complete = gevent.event.Event()
        self.done = gevent.event.Event()

        self._sync_objects = SyncObjects()
        self._requests = RequestCollection()
        self._derived_objects = DerivedObjects()

        ctx = zmq.Context(1)
        pub = ctx.socket(zmq.PUB)
        pub.connect('tcp://127.0.0.1:7003')
        self._notification_socket = pub

        self._notifier = notifier

        self._request_factories = {
            OSD: OsdRequestFactory,
            POOL: PoolRequestFactory
        }

        self._persister = persister

    def stop(self):
        log.info("%s stopping" % self.__class__.__name__)
        self._complete.set()

    def list_requests(self):
        return self._requests.get_all()

    def get_request(self, request_id):
        return self._requests.get_by_id(request_id)

    def get_sync_object(self, object_type):
        return self._sync_objects.get(object_type).data

    def get_derived_object(self, object_type):
        return self._derived_objects.get(object_type)

    def _run(self):
        event = salt.utils.event.MasterEvent(SALT_RUN_PATH)

        while not self._complete.is_set():
            ev = event.get_event(full=True)

            if ev is not None:
                data = ev['data']
                tag = ev['tag']
                log.debug("Event tag=%s" % tag)

                # I am interested in the following tags:
                # - salt/job/<jid>/ret/<minion id> where jid is one that I started
                #   (this includes ceph.rados_command and ceph.get_cluster_object)
                # - ceph/heartbeat/<fsid> where fsid is my fsid

                try:
                    if tag.startswith("ceph/heartbeat/{0}".format(self.fsid)):
                        # A ceph.heartbeat beacon
                        self.on_heartbeat(data['id'], data['data'])
                    elif re.match("^salt/job/\d+/ret/[^/]+$", tag):
                        # It would be much nicer to put the FSID at the start of
                        # the tag, if salt would only let us add custom tags to our jobs.
                        # Instead we enforce a convention that all calamari jobs must include
                        # fsid in their return value.
                        if 'fsid' not in data['return'] or data['return']['fsid'] != self.fsid:
                            log.debug("Ignoring job return, not for my FSID")
                            continue

                        if data['fun'] == 'ceph.get_cluster_object':
                            # A ceph.get_cluster_object response
                            # FIXME: ordering: should be tracking ongoing jids for each type of object
                            # we might have a sync out for, and
                            # FIXME: filtering: chop these down to only the jobs for this cluster, ideally
                            # I would like to prefix my cluster ID to JIDs
                            if not data['success']:
                                log.error("on_sync_object: failure from %s: %s" % (data['id'], data['return']))
                                continue
                            self.on_sync_object(data['id'], data['return'])
                        elif 'ceph.rados_commands':
                            # A ceph.rados_commands response
                            # FIXME: we'll get KeyErrors here if it's a JID from another ClusterMonitor,
                            # which is handled but generates nasty backtraces in the logs.  We should
                            # be explicitly checking that this command belongs to use (I *really* wish
                            # I could explicitly add to the tags of salt jobs to prefix with FSID).
                            self.on_completion(data)
                    else:
                        # This does not concern us, ignore it
                        pass
                except:
                    # Because this is our main event handling loop, swallow exceptions
                    # instead of letting them end the world.
                    log.exception("Exception handling message with tag %s" % tag)
                    log.debug("Message content: %s" % data)

        log.info("%s complete" % self.__class__.__name__)
        self.done.set()

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
                log.info("Advanced version %s/%s %s->%s" % (self.fsid, sync_type.str, old_version, new_version))

                # We are out of date: request an up to date copy
                client = salt.client.LocalClient(SALT_CONFIG_PATH)
                client.run_job(minion_id, 'ceph.get_cluster_object',
                               condition_kwarg([], {'cluster_name': cluster_data['name'],
                                                    'sync_type': sync_type.str,
                                                    'since': old_version}))

        # persistence.heartbeat()
        self.update_time = datetime.datetime.utcnow().replace(tzinfo=utc)

    def inject_sync_object(self, sync_type, version, data):
        sync_type = SYNC_OBJECT_STR_TYPE[sync_type]
        self._sync_objects.set_map(sync_type, version, data)

        # The frontend would like us to maintain some derived objects that
        # munge together the PG and OSD maps into an easier-to-consume form.
        for generator in derived.generators:
            if sync_type in generator.depends:
                dependency_data = {}
                for t in generator.depends:
                    obj = self._sync_objects.get(t)
                    if obj is not None:
                        dependency_data[t] = obj.data
                    else:
                        dependency_data[t] = None

                if None not in dependency_data.values():
                    log.debug("Updating %s" % generator.__name__)
                    derived_objects = generator.generate(dependency_data)
                    self._derived_objects.update(derived_objects)

    def on_sync_object(self, minion_id, data):
        if minion_id != self._favorite_mon:
            log.debug("Ignoring map from %s, it is not my favourite (%s)" % (minion_id, self._favorite_mon))

        fsid = data['fsid']

        sync_type = SYNC_OBJECT_STR_TYPE[data['type']]

        if data['version'] != self._sync_objects.get_version(sync_type):
            log.info("Received new copy of %s/%s: %s" % (fsid, sync_type.str, data['version']))
            self._notifier.publish('ceph:sync', {
                'type': data['type'],
                'version': data['version'],
                'data': data['data']
            })

            self.inject_sync_object(data['type'], data['version'], data['data'])

            # While UserRequests are running, they need to be kept informed of new
            # map versions, since some requests don't complete until they've seen
            # a certain version of a map.
            self._requests.on_map(sync_type, self._sync_objects)

            # TODO: get datetime out of map instead of setting it to now
            if isinstance(data['version'], int):
                version = data['version']
            else:
                version = None
            self._persister.update(self.fsid, sync_type.str, version, datetime.datetime.now(tzutc()), data['data'])

    def on_completion(self, data):
        self._requests.on_completion(data)
        # FIXME: to protect against an on_sync_object resulting from a job
        # completion happening just before we process the job completion,
        # we should send a request on_map callbacks for all the maps it
        # may be interested in right after a job completion.  Or, we could
        # just pass all the maps into the job completion callback so that
        # it can explicitly do a there 'n' then check.

    def set_favorite(self, minion_id):
        self._favorite_mon = minion_id
        # TODO: for use when we have lost contact
        # with the existing favorite: if we had any
        # outstanding jobs which were using it, then
        # synthesize failures for them.

    def request(self, method, obj_type, *args, **kwargs):
        """
        Create and submit UserRequest for a create, update or delete.
        """
        try:
            request_factory = self._request_factories[obj_type](self)
        except KeyError:
            raise ValueError("{0} is not one of {1}".format(obj_type, self._request_factories.keys()))

        if self._favorite_mon is None:
            raise ClusterUnavailable("Ceph cluster is currently unavailable for commands")

        request = getattr(request_factory, method)(*args, **kwargs)
        self._requests.submit(request, self._favorite_mon)
        return {
            'request_id': request.id
        }

    def request_delete(self, obj_type, obj_id):
        return self.request('delete', obj_type, obj_id)

    def request_create(self, obj_type, attributes):
        return self.request('create', obj_type, attributes)

    def request_update(self, obj_type, obj_id, attributes):
        return self.request('update', obj_type, obj_id, attributes)
