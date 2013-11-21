import re
import uuid
from pytz import utc
from cthulhu.manager import derived
from cthulhu.manager.types import SYNC_OBJECT_STR_TYPE, SYNC_OBJECT_TYPES, CEPH_OBJECT_TYPES, OSD, POOL, OsdMap


import datetime
import traceback
import dateutil
from dateutil.tz import tzlocal
import threading
import threading2
import salt
import salt.utils.event
import salt.client
from salt.client import condition_kwarg
import zmq

#from cthulhu import persistence

from cthulhu.manager.log import log


SALT_CONFIG_PATH = './salt/etc/salt/master'
SALT_RUN_PATH = './salt/var/run/salt/master'
# FIXME: this should be a function of the ceph.heartbeat schedule period which
# we should query from the salt pillar
FAVORITE_TIMEOUT_S = 60


class ClusterUnavailable(Exception):
    pass


class PublishError(Exception):
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
        self._lock = threading.Lock()

    def set_map(self, typ, version, map_data):
        with self._lock:
            self._objects[typ] = typ(version, map_data)

    def get_version(self, typ):
        with self._lock:
            return self._objects[typ].version if self._objects[typ] else None

    def get(self, typ):
        with self._lock:
            return self._objects[typ]


class DerivedObjects(dict):
    """
    Store for items which we generate as a function of sync objects, decorated
    versions etc.  Basically just a dict with locking.
    """
    def __init__(self):
        super(DerivedObjects, self).__init__()
        self._lock = threading.Lock()

    def get(self, key, default=None):
        with self._lock:
            return super(DerivedObjects, self).get(key, default)

    def set(self, key, value):
        with self._lock:
            self[key] = value


class CompletionCondition(object):
    """
    A check associated with a COMPLETING UserRequest.  This is to be
    checked once at the time the UserRequest has entered the COMPLETING
    state, then again each time on of the dependency sync objects is updated.
    """

    # Which sync objects can affect this?
    depends = []

    def apply(self, sync_objects):
        """
        May indicate:

         - Complete (return True)
         - Not yet complete (return False)
         - Will never complete, or internal error (raise exception)
        """
        raise NotImplementedError()


class UserRequest(object):
    """
    A request acts on one or more Ceph-managed objects, i.e.
    mon, mds, osd, pg.

    Amist the terminology mess of 'jobs', 'commands', 'operations', this class
    is named for clarity: it's an operation at an end-user level of
    granularity, something that might be a button in the UI.

    UserRequests are usually remotely executed on a mon.  However, there
    may be a final step of updating the state of ClusterMonitor in order
    that subsequent REST API consumer reads return values consistent with
    the job having completed, e.g. waiting for the OSD map to be up
    to date before calling a pool creation complete.  For this reason,
    UserRequests have a local ID and completion state that is independent
    of their remote ID (salt jid).

    Requests have the following lifecycle:
     NEW object is created, knows where it should run what commands remotely, and what
         it should call back when remote commands complete.
     SUBMITTED remote commands have been published using salt and we have obtained a
               salt JID.
     COMPLETING remote commands have completed, and any completion conditions
                are now being awaited.
     COMPLETE no further action, this instance will remain constant from this point on.
              this does not indicate anything about success or failure.
    """

    NEW = 'new'
    SUBMITTED = 'submitted'
    COMPLETING = 'completing'
    COMPLETE = 'complete'
    states = [NEW, SUBMITTED, COMPLETING, COMPLETE]

    def __init__(self, minion_id, fsid, cluster_name, commands,
                 completion_callback=None, completion_condition=None):
        """
        Requiring cluster_name and fsid is redundant (ideally everything would
        speak in terms of fsid) but convenient, because the librados interface
        wants a cluster name when you create a client, and otherwise we would
        have to look up via ceph.conf.

        :param completion_callback: A callable, invoked after remote execution is complete but
                                    before the state changes to COMPLETING.
        :param completion_condition: A CompletionCondition instance, which we will start testing
                                     one remote execution is complete and the completion callback
                                     has executed.
        """
        self.requested_at = datetime.datetime.now(tzlocal())

        # This is actually kind of overkill compared with having a counter,
        # somewhere but it's easy.
        self.id = uuid.uuid4().__str__()

        self._minion_id = minion_id
        self._fsid = fsid
        self._cluster_name = cluster_name
        self._commands = commands

        self._jid = None

        self.result = None
        self.state = self.NEW

        self._completion_callback = completion_callback
        self._completion_condition = completion_condition

    @property
    def submitted(self):
        return self.state == self.SUBMITTED

    @property
    def completing(self):
        return self.state == self.COMPLETING

    @property
    def jid(self):
        return self._jid

    def set_completion_condition(self, condition):
        """
        Set a completion condition after construction, e.g. if
        the parameters for completion are not known until after
        the remote execution completes.
        """
        assert not self._completion_condition
        self._completion_condition = condition

    def submit(self):
        """
        Start remote execution phase by publishing a job to salt.
        """
        log.debug("Request.submit: %s/%s/%s" % (self._minion_id, self._cluster_name, self._commands))
        assert not self.submitted

        client = salt.client.LocalClient(SALT_CONFIG_PATH)
        pub_data = client.run_job(self._minion_id, 'ceph.rados_commands', [self._fsid, self._cluster_name, self._commands])
        if not pub_data:
            # FIXME: LocalClient uses 'print' to record the
            # details of what went wrong :-(
            raise PublishError("Failed to publish job")
        self._jid = pub_data['jid']

        self.state = self.SUBMITTED

    def complete_jid(self, result):
        """
        Call this when remote execution is done.
        """
        self.result = result
        log.info("Request %s JID %s completed with result=%s" % (self.id, self._jid, self.result))
        if self._completion_callback:
            try:
                log.debug("Request %s calling completion callback" % self.id)
                self._completion_callback(self)
            except:
                log.exception("Calling completion callback for %s/%s" % (self.id, self.jid))
                # TODO: mark errored
                self.complete()

        if not self._completion_condition:
            log.debug("Request %s no completion condition skipping to complete" % self.id)
            self.complete()
        else:
            log.debug("Request %s going to state COMPLETING until condition is met" % self.id)
            self.state = self.COMPLETING

    @property
    def completion_condition(self):
        return self._completion_condition

    def complete(self):
        """
        Call this when:
         - Remote execution is done
         - Completion callback has been called
         - Completion condition has been met
        """
        self.state = self.COMPLETE


class OsdMapModifyingRequest(UserRequest):
    """
    Specialization of UserRequest which waits for Calamari's copy of
    the OsdMap sync object to catch up after execution of RADOS commands.
    """

    def __init__(self, minion_id, fsid, cluster_name, commands):
        super(OsdMapModifyingRequest, self).__init__(minion_id, fsid, cluster_name, commands)

        class OsdVersionCompletion(object):
            """
            A CompletionCondition which waits for the synchronized
            OSD map version to be >= a certain value.
            """

            depends = [OsdMap]

            def __init__(self, version):
                self._version = version

            def apply(self, sync_objects):
                osd_map = sync_objects.get(OsdMap)
                result = osd_map.version >= self._version
                if result:
                    log.debug("OsdVersionCompletion passed (%s >= %s)" % (osd_map.version, self._version))
                else:
                    log.debug("OsdVersionCompletion pending (%s < %s)" % (osd_map.version, self._version))
                return result

        def completion(request):
            """
            When the pool creation command has completed, set a completion
            condition for the calamari server to wait for the post-creation
            version of the OSD map to get synced up.
            """

            # TODO: to be snappier, instead of waiting for the OSD map to just show up,
            # send out a request for it here.  To avoid redundant/overlapping requests
            # will probaly want to have SyncObjects track which objects we're waiting
            # for and ignore requests to get objects which we're already getting.

            post_create_version = request.result['versions']['osd_map']
            log.debug("Request %s: Adding a completion condition for OSD map version %s" %
                      (request.id, post_create_version))
            request.set_completion_condition(OsdVersionCompletion(post_create_version))

        self._completion_callback = completion


class RequestCollection(object):
    """
    Manage a collection of UserRequests, indexed by
    salt JID and request ID.

    Requests don't appear in this collection until they have
    made it at least as far as SUBMITTED state.

    """
    def __init__(self):
        super(RequestCollection, self).__init__()
        self._shlock = threading2.SHLock()

        self._by_request_id = {}
        self._by_jid = {}

    def put(self, request):
        assert request.submitted

        self._shlock.acquire(shared=False)
        try:
            self._by_request_id[request.id] = request
            self._by_jid[request.jid] = request
        finally:
            self._shlock.release()

    def get_by_id(self, request_id):
        self._shlock.acquire(shared=True)
        try:
            return self._by_request_id[request_id]
        finally:
            self._shlock.release()

    def get_by_jid(self, jid):
        self._shlock.acquire(shared=True)
        try:
            return self._by_jid[jid]
        finally:
            self._shlock.release()

    def get_all(self, state=None):
        self._shlock.acquire(shared=True)
        try:
            if not state:
                return self._by_request_id.values()
            else:
                return [r for r in self._by_request_id.values() if r.state == state]
        finally:
            self._shlock.release()


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
        self._update_time = None

        self._last_heartbeat = {}

        self._requests = RequestCollection()

        self._complete = threading.Event()

        self._sync_objects = SyncObjects()

        self._derived_objects = DerivedObjects()

        ctx = zmq.Context(1)
        pub = ctx.socket(zmq.PUB)
        pub.connect('tcp://127.0.0.1:7003')
        self._notification_socket = pub

        self._notifier = notifier

    def get_request(self, request_id):
        return self._requests.get_by_id(request_id)

    def get_sync_object(self, object_type):
        return self._sync_objects.get(object_type).data

    def get_derived_object(self, object_type):
        return self._derived_objects.get(object_type)

    def run(self):
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
                    if tag.startswith("ceph/heartbeat/{0}".format(self._fsid)):
                        # A ceph.heartbeat beacon
                        self.on_heartbeat(data['id'], data['data'])
                    elif re.match("^salt/job/\d+/ret/[^/]+$", tag):
                        # It would be much nicer to put the FSID at the start of
                        # the tag, if salt would only let us add custom tags to our jobs.
                        # Instead we enforce a convention that all calamari jobs must include
                        # fsid in their return value.
                        if 'fsid' not in data['return'] or data['return']['fsid'] != self._fsid:
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
                            self.on_completion(data)
                    else:
                        # This does not concern us, ignore it
                        pass
                except:
                    # Because this is our main event handling loop,
                    log.exception("Exception handling message with tag %s" % tag)
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

#        persistence.heartbeat()
        self._update_time = datetime.datetime.utcnow().replace(tzinfo=utc)

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

            self._sync_objects.set_map(sync_type, data['version'], data['data'])

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

            # UserRequests may post CompletionConditions which depend on the state
            # of sync objects, check if there are any of these out there and
            for user_request in self._requests.get_all(state=UserRequest.COMPLETING):
                cc = user_request.completion_condition
                if sync_type in cc.depends:
                    try:
                        if cc.apply(self._sync_objects):
                            user_request.complete()
                    except:
                        # TODO: mark errored
                        user_request.complete()

            # TODO: for this sync object and any regenerated derived objects, push
            # them to the queue for persistence.

    def on_completion(self, data):
        jid = data['jid']
        result = data['return']
        log.debug("on_completion: jid=%s data=%s" % (jid, data))

        request = self._requests.get_by_jid(jid)

        if not data['success']:
            log.error("Remote execution failed for request %s: %s" % (request.id, result))
            # TODO: mark errored
            request.complete()
        else:

            if request.state != UserRequest.SUBMITTED:
                # Unexpected, ignore.
                log.error("Received completion for request %s/%s in state %s" % (
                    request.id, request.jid, request.state
                ))
                return

            request.complete_jid(result)

            if request.state == UserRequest.COMPLETING:
                try:
                    if request.completion_condition.apply(self._sync_objects):
                        request.complete()
                except:
                    log.exception("Checking completion condition")
                    # TODO: mark errored
                    request.complete()

        # TODO: publish this at actual completion rather than jid completion
        #self._notifier.publish('ceph:completion', {'jid': jid})

    def set_favorite(self, minion_id):
        self._favorite_mon = minion_id
        # TODO: for use when we have lost contact
        # with the existing favorite: if we had any
        # outstanding jobs which were using it, then
        # synthesize failures for them.

    def request_create(self, obj_type, attributes):
        if obj_type not in CEPH_OBJECT_TYPES:
            raise ValueError("{0} is not one of {1}".format(obj_type, CEPH_OBJECT_TYPES))

        if self._favorite_mon is None:
            raise ClusterUnavailable("Ceph cluster is currently unavailable for commands")

        if obj_type == POOL:
            # TODO: handle errors in a way that caller can show to a user, e.g.
            # if the name is wrong we should be sending a structured errors dict
            # that they can use to associate the complaint with the 'name' field.
            commands = [('osd pool create', {'pool': attributes['name'], 'pg_num': attributes['pg_num']})]
            req = OsdMapModifyingRequest(self._favorite_mon, self._fsid, self._name, commands)

            req.submit()
            self._requests.put(req)
            return {
                'request_id': req.id
            }
        else:
            raise NotImplementedError(obj_type)

    def _resolve_pool(self, pool_id):
        for pool in self._sync_objects.get(OsdMap).data['pools']:
            if pool['pool'] == pool_id:
                return pool
        else:
            raise ValueError("Pool %s not found" % pool_id)

    def request_delete(self, obj_type, obj_id):
        if obj_type not in CEPH_OBJECT_TYPES:
            raise ValueError("{0} is not one of {1}".format(obj_type, CEPH_OBJECT_TYPES))

        if self._favorite_mon is None:
            raise ClusterUnavailable("Ceph cluster is currently unavailable for commands")

        if obj_type == POOL:

            # Resolve pool ID to name
            pool_name = self._resolve_pool(obj_id)['pool_name']

            # TODO: perhaps the REST API should have something in the body to
            # make it slightly harder to accidentally delete a pool, to respect
            # the severity of this operation since we're hiding the --yes-i-really-really-want-to
            # stuff here
            # TODO: handle errors in a way that caller can show to a user, e.g.
            # if the name is wrong we should be sending a structured errors dict
            # that they can use to associate the complaint with the 'name' field.
            commands = [('osd pool delete', {'pool': pool_name, 'pool2': pool_name, 'sure': '--yes-i-really-really-mean-it'})]
            req = OsdMapModifyingRequest(self._favorite_mon, self._fsid, self._name, commands)

            req.submit()
            self._requests.put(req)
            return {
                'request_id': req.id
            }
        else:
            raise NotImplementedError(obj_type)

    def request_update(self, obj_type, obj_id, attributes):
        """

        This function requires a read lock on the cluster map.
        This function requires a read lock and briefly a write lock on the request collection.

        :param obj_type: OSD, MDS, MON or PG
        :param patches: List of dicts, each dict must have at least 'id' attribute.
        """

        if obj_type not in CEPH_OBJECT_TYPES:
            raise ValueError("{0} is not one of {1}".format(obj_type, CEPH_OBJECT_TYPES))

        if self._favorite_mon is None:
            raise ClusterUnavailable("Ceph cluster is currently unavailable for commands")

        if obj_type == OSD:
            commands = []
            if attributes['in'] == 0:
                commands.append(('osd out', {'ids': [attributes['id'].__str__()]}))
            else:
                commands.append(('osd out', {'ids': [attributes['id'].__str__()]}))

            # TODO: provide some per-object-type ability to emit human readable descriptions
            # of what we are doing.

            # TOOD: provide some machine-readable indication of which objects are affected
            # by a particular request.
            # Perhaps subclass Request for each type of object, and have that subclass provide
            # both the patches->commands mapping and the human readable and machine readable
            # descriptions of it?
            req = OsdMapModifyingRequest(self._favorite_mon, self._fsid, self._name, commands)

            try:
                req.submit()
            except ClusterUnavailable:
                # TODO: Handle mon going away: interrogate salt to find a connected mon
                # and make that the new favourite.
                raise

            self._requests.put(req)
            return {
                'request_id': req.id
            }
        elif obj_type == POOL:
            # TODO: this is a primitive form of adding PGs, not yet sufficient for
            # real use because it leaves pgp_num unset.
            commands = []
            if 'pg_num' in attributes:
                # TODO: also set pgp_num, although ceph annoyingly doesn't
                # let us do this until all the PGs are created, unless there
                # is some hidden way to set it at the same time as pg_Num?
                pool_name = self._resolve_pool(obj_id)['pool_name']
                commands.append(('osd pool set', {
                    'pool': pool_name,
                    'var': 'pg_num',
                    'val': attributes['pg_num']
                }))
            else:
                raise NotImplementedError(attributes)

            # TODO: provide some per-object-type ability to emit human readable descriptions
            # of what we are doing.

            # TOOD: provide some machine-readable indication of which objects are affected
            # by a particular request.
            # Perhaps subclass Request for each type of object, and have that subclass provide
            # both the patches->commands mapping and the human readable and machine readable
            # descriptions of it?
            req = OsdMapModifyingRequest(self._favorite_mon, self._fsid, self._name, commands)

            try:
                req.submit()
            except ClusterUnavailable:
                # TODO: Handle mon going away: interrogate salt to find a connected mon
                # and make that the new favourite.
                raise

            self._requests.put(req)

            return {
                'request_id': req.id
            }
        else:
            raise NotImplementedError(obj_type)