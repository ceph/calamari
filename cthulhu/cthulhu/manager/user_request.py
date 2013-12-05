from contextlib import contextmanager
import datetime
import uuid
from dateutil.tz import tzlocal
import salt
import salt.client
import threading2
from cthulhu.config import SALT_CONFIG_PATH
from cthulhu.log import log
from cthulhu.manager.types import OsdMap


class PublishError(Exception):
    pass


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
    COMPLETE = 'complete'
    states = [NEW, SUBMITTED, COMPLETE]

    def __init__(self, fsid, cluster_name, commands,
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

        self._minion_id = None
        self._fsid = fsid
        self._cluster_name = cluster_name
        self._commands = commands

        self._jid = None

        self.state = self.NEW
        self.result = None
        self.error = False

    @property
    def jid(self):
        return self._jid

    def submit(self, minion_id):
        """
        Start remote execution phase by publishing a job to salt.
        """
        log.debug("Request.submit: %s/%s/%s" % (minion_id, self._cluster_name, self._commands))
        assert self.state == self.NEW

        client = salt.client.LocalClient(SALT_CONFIG_PATH)
        pub_data = client.run_job(minion_id, 'ceph.rados_commands',
                                  [self._fsid, self._cluster_name, self._commands])
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

        # This is a default behaviour for UserRequests which don't override this method:
        # assume completion of a JID means the job is now done.
        self.complete()

    def complete(self, error=False):
        """
        Call this when you're all done
        """
        self.state = self.COMPLETE
        self.error = error

    def on_map(self, sync_type, sync_objects):
        pass


class OsdMapModifyingRequest(UserRequest):
    """
    Specialization of UserRequest which waits for Calamari's copy of
    the OsdMap sync object to catch up after execution of RADOS commands.
    """

    def __init__(self, fsid, cluster_name, commands):
        super(OsdMapModifyingRequest, self).__init__(fsid, cluster_name, commands)
        self._await_version = None

    def complete_jid(self, result):
        # My remote work is done, record the version of the map that I will wait for
        # and start waiting for it.
        self.result = result
        self._await_version = result['versions']['osd_map']

        # TODO: to be snappier, instead of waiting for the OSD map to just show up,
        # send out a request for it here.  To avoid redundant/overlapping requests
        # will probaly want to have SyncObjects track which objects we're waiting
        # for and ignore requests to get objects which we're already getting.

    def on_map(self, sync_type, sync_objects):
        if sync_type != OsdMap:
            return

        osd_map = sync_objects.get(OsdMap)
        ready = osd_map.version >= self._await_version
        if ready:
            log.debug("OsdMapModifyingRequest passed (%s >= %s)" % (osd_map.version, self._await_version))
            self.complete()
        else:
            log.debug("OsdMapModifyingRequest pending (%s < %s)" % (osd_map.version, self._await_version))


class RequestCollection(object):
    """
    Manage a collection of UserRequests, indexed by
    salt JID and request ID.
    """

    def __init__(self):
        super(RequestCollection, self).__init__()
        self._shlock = threading2.SHLock()

        self._by_request_id = {}
        self._by_jid = {}

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

    def submit(self, request, minion):
        """
        Submit a request and store it.  Do this in one operation
        to hold the lock over both operations, otherwise a response
        to a job could arrive before the request was filed here.
        """
        self._shlock.acquire(shared=False)
        request.submit(minion)
        try:
            self._by_request_id[request.id] = request
            self._by_jid[request.jid] = request
        finally:
            self._shlock.release()

    def on_map(self, sync_type, sync_objects):
        requests = self.get_all(state=UserRequest.SUBMITTED)
        for request in requests:

            with self.update_index(request):
                request.on_map(sync_type, sync_objects)

    def update_index(self, request):
        """
        Context manager to acquire across request-modifying operations
        to ensure lookups like by_jid are up to date if requests
        were modified in the process
        """

        @contextmanager
        def update():
            # Take write lock across on_map + subsequent by_jid update,
            # in order to ensure by_jid is up to date before any response
            # to new jids can arrive.
            self._shlock.acquire(shared=False)
            try:
                old_jid = request.jid
                yield
                # Update by_jid in case this triggered a new job
                if request.jid != old_jid:
                    if old_jid:
                        del self._by_jid[old_jid]
                    if request.jid:
                        self._by_jid[request.jid] = request
            finally:
                self._shlock.release()

        return update()

    def on_completion(self, data):
        jid = data['jid']
        result = data['return']
        log.debug("on_completion: jid=%s data=%s" % (jid, data))

        request = self.get_by_jid(jid)

        # TODO: tag some detail onto the UserRequest object
        # when a failure occurs
        if not data['success']:
            log.error("Remote execution failed for request %s: %s" % (request.id, result))
            request.complete(error=True)
        else:
            if request.state != UserRequest.SUBMITTED:
                # Unexpected, ignore.
                log.error("Received completion for request %s/%s in state %s" % (
                    request.id, request.jid, request.state
                ))
                return

            try:
                with self.update_index(request):
                    request.complete_jid(result)
            except Exception:
                # Ensure that a misbehaving piece of code in a UserRequest subclass
                # results in a terminated job, not a zombie job
                log.exception("Calling complete_jid for %s/%s" % (request.id, request.jid))
                request.complete(error=True)
