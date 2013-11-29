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

    def submit(self, minion_id):
        """
        Start remote execution phase by publishing a job to salt.
        """
        log.debug("Request.submit: %s/%s/%s" % (minion_id, self._cluster_name, self._commands))
        assert not self.submitted

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

    def __init__(self, fsid, cluster_name, commands):
        super(OsdMapModifyingRequest, self).__init__(fsid, cluster_name, commands)

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
