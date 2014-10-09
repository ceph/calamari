
import re
import datetime

from pytz import utc
import gevent.greenlet
import gevent.event

from calamari_common.salt_wrapper import condition_kwarg, LocalClient, SaltEventSource

from cthulhu.gevent_util import nosleep, nosleep_mgr
from cthulhu.log import log
from cthulhu.manager.crush_node_request_factory import CrushNodeRequestFactory
from cthulhu.manager.crush_request_factory import CrushRequestFactory
from cthulhu.manager.osd_request_factory import OsdRequestFactory
from cthulhu.manager.pool_request_factory import PoolRequestFactory
from cthulhu.manager.plugin_monitor import PluginMonitor
from calamari_common.types import CRUSH_NODE, CRUSH_MAP, SYNC_OBJECT_STR_TYPE, SYNC_OBJECT_TYPES, OSD, POOL, OsdMap, MdsMap, MonMap
from cthulhu.manager import config, salt_config
from cthulhu.util import now


FAVORITE_TIMEOUT_FACTOR = int(config.get('cthulhu', 'favorite_timeout_factor'))


class ClusterUnavailable(Exception):
    pass


class SyncObjects(object):
    """
    A collection of versioned objects, keyed by their class (which
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

    def on_version(self, reported_by, sync_type, new_version):
        """
        Notify me that a particular version of a particular map exists.

        I may choose to initiate RPC to retrieve the map
        """
        log.debug("SyncObjects.on_version %s/%s/%s" % (reported_by, sync_type.str, new_version))
        old_version = self.get_version(sync_type)
        if sync_type.cmp(new_version, old_version) > 0:
            known_version = self._known_versions[sync_type]
            if sync_type.cmp(new_version, known_version) > 0:
                # We are out of date: request an up to date copy
                log.info("Advanced known version %s/%s %s->%s" % (
                    self._cluster_name, sync_type.str, known_version, new_version))
                self._known_versions[sync_type] = new_version
            else:
                log.info("on_version: %s is newer than %s" % (new_version, old_version))

            # If we already have a request out for this type of map, then consider
            # cancelling it if we've already waited for a while.
            if self._fetching_at[sync_type] is not None:
                if now() - self._fetching_at[sync_type] < self.FETCH_TIMEOUT:
                    log.info("Fetch already underway for %s" % sync_type.str)
                    return
                else:
                    log.warn("Abandoning fetch for %s started at %s" % (
                        sync_type.str, self._fetching_at[sync_type]))

            log.info("on_version: fetching %s/%s from %s, currently got %s, know %s" % (
                sync_type, new_version, reported_by, old_version, known_version
            ))
            self.fetch(reported_by, sync_type)

    def fetch(self, minion_id, sync_type):
        log.debug("SyncObjects.fetch: %s/%s" % (minion_id, sync_type))
        if minion_id is None:
            # We're probably being replayed to from the database
            log.warn("SyncObjects.fetch called with minion_id=None")
            return

        self._fetching_at[sync_type] = now()
        client = LocalClient(config.get('cthulhu', 'salt_config_path'))
        # TODO clean up unused 'since' argument
        pub_data = client.run_job(minion_id, 'ceph.get_cluster_object',
                                  condition_kwarg([], {'cluster_name': self._cluster_name,
                                                       'sync_type': sync_type.str,
                                                       'since': None}))
        if not pub_data:
            log.error("Failed to start fetch job %s/%s" % (minion_id, sync_type))
            # Don't throw an exception because if a fetch fails we should always
        else:
            log.debug("SyncObjects.fetch: jid=%s minions=%s" % (pub_data['jid'], pub_data['minions']))

    def on_fetch_complete(self, minion_id, sync_type, version, data):
        """
        :return A SyncObject if this version was new to us, else None
        """
        log.debug("SyncObjects.on_fetch_complete %s/%s/%s" % (minion_id, sync_type.str, version))
        self._fetching_at[sync_type] = None

        # A fetch might give us a newer version than we knew we had asked for
        if sync_type.cmp(version, self._known_versions[sync_type]) > 0:
            self._known_versions[sync_type] = version

        # Don't store this if we already got something newer
        if sync_type.cmp(version, self.get_version(sync_type)) <= 0:
            log.warn("Ignoring outdated update %s/%s from %s" % (sync_type.str, version, minion_id))
            new_object = None
        else:
            log.info("Got new version %s/%s" % (sync_type.str, version))
            new_object = self.set_map(sync_type, version, data)

        # This might not be the latest: if it's not, send out another fetch
        # right away
        if sync_type.cmp(self._known_versions[sync_type], version) > 0:
            self.fetch(minion_id, sync_type)

        return new_object


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

    def __init__(self, fsid, cluster_name, notifier, persister, servers, eventer, requests):
        super(ClusterMonitor, self).__init__()

        self.fsid = fsid
        self.name = cluster_name
        self.update_time = datetime.datetime.utcnow().replace(tzinfo=utc)

        self._notifier = notifier
        self._persister = persister
        self._servers = servers
        self._eventer = eventer
        self._requests = requests

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

        self._plugin_monitor = PluginMonitor(servers)
        self._ready = gevent.event.Event()

    def ready(self):
        """
        Block until the ClusterMonitor is ready to receive salt events
        """
        self._ready.wait()

    def stop(self):
        log.info("%s stopping" % self.__class__.__name__)
        self._complete.set()

    @nosleep
    def get_sync_object_data(self, object_type):
        """
        :param object_type: A SyncObject subclass
        :returns: a json-serializable object
        """
        return self._sync_objects.get_data(object_type)

    @nosleep
    def get_sync_object(self, object_type):
        """
        :param object_type: A SyncObject subclass
        :returns: a SyncObject instance
        """
        return self._sync_objects.get(object_type)

    def _run(self):
        self._plugin_monitor.start()

        self._ready.set()
        log.debug("ClusterMonitor._run: ready")

        event = SaltEventSource(log, salt_config)

        while not self._complete.is_set():
            # No salt tag filtering: https://github.com/saltstack/salt/issues/11582
            ev = event.get_event(full=True)

            if ev is not None:
                data = ev['data']
                tag = ev['tag']
                log.debug("_run.ev: %s/tag=%s" % (data['id'] if 'id' in data else None, tag))

                # I am interested in the following tags:
                # - salt/job/<jid>/ret/<minion id> where jid is one that I started
                #   (this includes ceph.rados_command and ceph.get_cluster_object)
                # - ceph/cluster/<fsid> where fsid is my fsid

                try:
                    if tag.startswith("ceph/cluster/{0}".format(self.fsid)):
                        # A ceph.heartbeat beacon
                        self.on_heartbeat(data['id'], data['data'])
                    elif re.match("^salt/job/\d+/ret/[^/]+$", tag):
                        if data['fun'] == "saltutil.running":
                            # Update on what jobs are running
                            # It would be nice to filter these down to those which really are for
                            # this cluster, but as long as N_clusters and N_jobs are reasonably small
                            # it's not an efficiency problem.
                            self._requests.on_tick_response(data['id'], data['return'])

                        # It would be much nicer to put the FSID at the start of
                        # the tag, if salt would only let us add custom tags to our jobs.
                        # Instead we enforce a convention that all calamari jobs must include
                        # fsid in their return value.
                        if (not isinstance(data, dict)) or not isinstance(data['return'], dict):
                            # Something not formatted for ClusterMonitor
                            log.warning("Ignoring event %s" % tag)
                            continue

                        if 'fsid' not in data['return'] or data['return']['fsid'] != self.fsid:
                            # Something for a different ClusterMonitor
                            log.debug("Ignoring job return, not for my FSID")
                            continue

                        if data['fun'] == 'ceph.get_cluster_object':
                            # A ceph.get_cluster_object response
                            if not data['success']:
                                log.error("on_sync_object: failure from %s: %s" % (data['id'], data['return']))
                                continue

                            self.on_sync_object(data['id'], data['return'])
                        else:
                            log.warning("Unexpected function '%s' (%s)" % (data['fun'], tag))
                    else:
                        # This does not concern us, ignore it
                        pass
                except:
                    # Because this is our main event handling loop, swallow exceptions
                    # instead of letting them end the world.
                    log.exception("Exception handling message with tag %s" % tag)
                    log.debug("Message content: %s" % data)

        log.info("%s complete" % self.__class__.__name__)
        self._plugin_monitor.stop()
        self._plugin_monitor.join()
        self.done.set()

    def _is_favorite(self, minion_id):
        """
        Check if this minion is the one which we are currently treating
        as the primary source of updates, and promote it to be the
        favourite if the favourite has not sent a heartbeat since
        cthulhu->favorite_timeout_s.

        :return True if this minion was the favorite or has just been
                promoted.
        """
        t_now = now()
        self._last_heartbeat[minion_id] = t_now

        if self._favorite_mon is None:
            log.debug("%s is my new favourite" % minion_id)
            self._set_favorite(minion_id)
            return True
        elif minion_id != self._favorite_mon:
            # Consider whether this minion should become my new favourite: has it been
            # too long since my current favourite reported in?
            time_since = t_now - self._last_heartbeat[self._favorite_mon]
            favorite_timeout_s = self._servers.get_contact_period(self._favorite_mon) * FAVORITE_TIMEOUT_FACTOR
            if time_since > datetime.timedelta(seconds=favorite_timeout_s):
                log.debug("My old favourite, %s, has not sent a heartbeat for %s: %s is my new favourite" % (
                    self._favorite_mon, time_since, minion_id
                ))
                self._set_favorite(minion_id)

        return minion_id == self._favorite_mon

    @nosleep
    def on_version(self, minion_id, sync_type, version):
        self._sync_objects.on_version(minion_id, sync_type, version)

    @nosleep
    def on_heartbeat(self, minion_id, cluster_data):
        """
        Handle a ceph.heartbeat from a minion.

        Heartbeats come from all servers, but we're mostly interested in those
        which come from a mon (and therefore have the 'clusters' attribute populated)
        as these tells us whether there are any new versions of cluster maps
        for us to fetch.
        """

        if not self._is_favorite(minion_id):
            log.debug('Ignoring cluster data from %s, it is not my favourite (%s)' % (minion_id, self._favorite_mon))
            return

        self.update_time = datetime.datetime.utcnow().replace(tzinfo=utc)

        log.debug('Checking for version increments in heartbeat from %s' % minion_id)
        for sync_type in SYNC_OBJECT_TYPES:
            self._sync_objects.on_version(
                minion_id,
                sync_type,
                cluster_data['versions'][sync_type.str])

    def inject_sync_object(self, minion_id, sync_type, version, data):
        sync_type = SYNC_OBJECT_STR_TYPE[sync_type]
        old_object = self._sync_objects.get(sync_type)
        new_object = self._sync_objects.on_fetch_complete(minion_id, sync_type, version, data)

        if new_object:
            # The ServerMonitor is interested in cluster maps
            if sync_type == OsdMap:
                self._servers.on_osd_map(data)
            elif sync_type == MonMap:
                self._servers.on_mon_map(data)
            elif sync_type == MdsMap:
                self._servers.on_mds_map(self.fsid, data)

            self._eventer.on_sync_object(self.fsid, sync_type, new_object, old_object)

        return new_object

    @nosleep
    def on_sync_object(self, minion_id, data):
        if minion_id != self._favorite_mon:
            log.debug("Ignoring map from %s, it is not my favourite (%s)" % (minion_id, self._favorite_mon))

        assert data['fsid'] == self.fsid

        sync_object = data['data']

        sync_type = SYNC_OBJECT_STR_TYPE[data['type']]
        new_object = self.inject_sync_object(minion_id, data['type'], data['version'], sync_object)
        if new_object:
            self._requests.on_map(self.fsid, sync_type, new_object)
            self._persister.update_sync_object(
                self.fsid,
                self.name,
                sync_type.str,
                new_object.version if isinstance(new_object.version, int) else None,
                now(), sync_object)
        else:
            log.warn("ClusterMonitor.on_sync_object: stale object received from %s" % minion_id)

    def _set_favorite(self, minion_id):
        assert minion_id != self._favorite_mon
        self._requests.fail_all(minion_id)

        self._favorite_mon = minion_id

    def _request(self, method, obj_type, *args, **kwargs):
        """
        Create and submit UserRequest for an apply, create, update or delete.
        """

        # nosleep during preparation phase (may touch ClusterMonitor/ServerMonitor state)
        request = None
        with nosleep_mgr():
            request_factory = self.get_request_factory(obj_type)

            if self._favorite_mon is None:
                raise ClusterUnavailable("Ceph cluster is currently unavailable for commands")

            request = getattr(request_factory, method)(*args, **kwargs)

        if request:
            # sleeps permitted during terminal phase of submitting, because we're
            # doing I/O to the salt master to kick off
            self._requests.submit(request, self._favorite_mon)
            return {
                'request_id': request.id
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
        return self.get_request_factory(object_type).get_valid_commands(obj_ids)

    def get_request_factory(self, object_type):
        try:
            return self._request_factories[object_type](self)
        except KeyError:
            raise ValueError("{0} is not one of {1}".format(object_type, self._request_factories.keys()))
