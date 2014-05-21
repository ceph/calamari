from contextlib import contextmanager
from gevent.lock import RLock
import datetime
from salt.client import LocalClient

from cthulhu.gevent_util import nosleep
from cthulhu.manager.user_request import UserRequest
from cthulhu.log import log
from cthulhu.util import now
from cthulhu.manager import config

TICK_PERIOD = 20


class RequestCollection(object):
    """
    Manage a collection of UserRequests, indexed by
    salt JID and request ID.

    Unlike most of cthulhu, this class contains a lock, which
    is used in all entry points which may sleep (anything which
    progresses a UserRequest might involve I/O to create jobs
    in the salt master), so that they don't go to sleep and
    wake up in a different world.
    """

    def __init__(self, manager):
        super(RequestCollection, self).__init__()

        self._by_request_id = {}
        self._by_jid = {}
        self._lock = RLock()

        self._manager = manager

    def get_by_id(self, request_id):
        return self._by_request_id[request_id]

    def get_by_jid(self, jid):
        return self._by_jid[jid]

    def get_all(self, state=None):
        if not state:
            return self._by_request_id.values()
        else:
            return [r for r in self._by_request_id.values() if r.state == state]

    def tick(self):
        """
        For walltime-based monitoring of running requests.  Long-running requests
        get a periodic call to saltutil.running to verify that things really
        are still happening.
        """

        if not self._by_jid:
            return
        else:
            log.debug("RequestCollection.tick: %s JIDs underway" % len(self._by_jid))

        # Identify JIDs who haven't had a saltutil.running reponse for too long.
        # Kill requests in a separate phase because request:JID is not 1:1
        stale_jobs = set()
        _now = now()
        for request in self._by_jid.values():
            if _now - request.alive_at > datetime.timedelta(seconds=TICK_PERIOD * 3):
                log.error("Request %s JID %s stale: now=%s, alive_at=%s" % (
                    request.id, request.jid, _now, request.alive_at
                ))
                stale_jobs.add(request)

        # Any identified stale jobs are errored out.
        for request in stale_jobs:
            with self._update_index(request):
                request.set_error("Lost contact")
                request.jid = None
                request.complete()

        # Identify minions associated with JIDs in flight
        query_minions = set()
        for jid, request in self._by_jid.items():
            query_minions.add(request.minion_id)

        # Attempt to emit a saltutil.running to ping jobs, next tick we
        # will see if we got updates to the alive_at attribute to indicate non-staleness
        if query_minions:
            log.info("RequestCollection.tick: sending saltutil.running to {0}".format(query_minions))
            client = LocalClient(config.get('cthulhu', 'salt_config_path'))
            pub_data = client.run_job(list(query_minions), 'saltutil.running', [], expr_form="list")
            if not pub_data:
                log.warning("Failed to publish saltutil.running to {0}".format(query_minions))

    def on_tick_response(self, minion_id, jobs):
        """
        Update the alive_at parameter of requests to record that they
        are still running remotely.

        :param jobs: The response from a saltutil.running
        """
        log.debug("RequestCollection.on_tick_response: %s from %s" % (len(jobs), minion_id))
        for job in jobs:
            try:
                request = self._by_jid[job['jid']]
            except KeyError:
                # Not one of mine, ignore it
                pass
            else:
                request.alive_at = now()

    def cancel(self, request_id):
        """
        Immediately mark a request as cancelled, and in the background
        try and cancel any outstanding JID for it.
        """
        request = self._by_request_id[request_id]
        with self._update_index(request):
            request.set_error("Cancelled")
            request.complete()

            if request.jid:
                client = LocalClient(config.get('cthulhu', 'salt_config_path'))
                client.run_job(request.minion_id, 'saltutil.kill_job',
                               [request.jid])
                # We don't check for completion or errors from kill_job, it's a best-effort thing.  If we're
                # cancelling something we will do our best to kill any subprocess but can't
                # any guarantees because running nodes may be out of touch with the calamari server.
                request.jid = None

    @nosleep
    def fail_all(self, failed_minion):
        """
        For use when we lose contact with the minion that was in use for running
        requests: assume all these requests are never going to return now.
        """
        for request in self.get_all(UserRequest.SUBMITTED):
            with self._update_index(request):
                request.set_error("Lost contact with server %s" % failed_minion)
                if request.jid:
                    log.error("Giving up on JID %s" % request.jid)
                    request.jid = None
                request.complete()

    def submit(self, request, minion):
        """
        Submit a request and store it.  Do this in one operation
        to hold the lock over both operations, otherwise a response
        to a job could arrive before the request was filed here.
        """
        with self._lock:
            request.submit(minion)
            self._by_request_id[request.id] = request
            self._by_jid[request.jid] = request
        self._manager.eventer.on_user_request_begin(request)

    def on_map(self, fsid, sync_type, sync_object):
        """
        Callback for when a new cluster map is available, in which
        we notify any interested ongoing UserRequests of the new map
        so that they can progress if they were waiting for it.
        """
        with self._lock:
            requests = self.get_all(state=UserRequest.SUBMITTED)
            for request in requests:
                if request.fsid != fsid:
                    pass

                try:
                    # If this is one of the types that this request
                    # is waiting for, invoke on_map.
                    for awaited_type in request.awaiting_versions.keys():
                        if awaited_type == sync_type:
                            with self._update_index(request):
                                request.on_map(sync_type, sync_object)
                except Exception as e:
                    log.exception("Request %s threw exception in on_map", request.id)
                    if request.jid:
                        log.error("Abandoning job {0}".format(request.jid))
                        request.jid = None

                    request.set_error("Internal error %s" % e)
                    request.complete()

                if request.state == UserRequest.COMPLETE:
                    self._manager.eventer.on_user_request_complete(request)

    def on_completion(self, data):
        """
        Callback for when a salt/job/<jid>/ret event is received, in which
        we find the UserRequest that created the job, and inform it of
        completion so that it can progress.
        """
        with self._lock:
            jid = data['jid']
            result = data['return']
            log.debug("on_completion: jid=%s data=%s" % (jid, data))

            try:
                request = self.get_by_jid(jid)
                log.debug("on_completion: jid %s belongs to request %s" % (jid, request.id))
            except KeyError:
                log.warning("on_completion: unknown jid {0}".format(jid))
                return

            if not data['success']:
                # This indicates a failure at the salt level, i.e. job threw an exception
                log.error("Remote execution failed for request %s: %s" % (request.id, result))
                if isinstance(result, dict):
                    # Handler ran and recorded an error for us
                    request.set_error(result['error_status'])
                else:
                    # An exception, probably, stringized by salt for us
                    request.set_error(result)
                request.complete()
            elif result['error']:
                # This indicates a failure within ceph.rados_commands which was caught
                # by our code, like one of our Ceph commands returned an error code.
                # NB in future there may be UserRequest subclasses which want to receive
                # and handle these errors themselves, so this branch would be refactored
                # to allow that.
                log.error("Request %s experienced an error: %s" % (request.id, result['error_status']))
                request.jid = None
                request.set_error(result['error_status'])
                request.complete()
            else:
                if request.state != UserRequest.SUBMITTED:
                    # Unexpected, ignore.
                    log.error("Received completion for request %s/%s in state %s" % (
                        request.id, request.jid, request.state
                    ))
                    return

                try:
                    with self._update_index(request):
                        old_jid = request.jid
                        request.complete_jid(result)
                        assert request.jid != old_jid

                        # After a jid completes, requests may start waiting for cluster
                        # map updates, we ask ClusterMonitor to hurry up and get them on
                        # behalf of the request.
                        if request.awaiting_versions:
                            assert request.fsid
                            cluster_monitor = self._manager.clusters[request.fsid]
                            for sync_type, version in request.awaiting_versions.items():

                                if version is not None:
                                    log.debug("Notifying cluster of awaited version %s/%s" % (sync_type.str, version))
                                    cluster_monitor.on_version(data['id'], sync_type, version)

                            # The request may be waiting for an epoch that we already have, if so
                            # give it to the request right away
                            for sync_type, want_version in request.awaiting_versions.items():
                                sync_object = cluster_monitor.get_sync_object(sync_type)
                                if want_version and sync_type.cmp(sync_object.version, want_version) >= 0:
                                    log.info("Awaited %s %s is immediately available" % (sync_type, want_version))
                                    request.on_map(sync_type, sync_object)

                except Exception as e:
                    # Ensure that a misbehaving piece of code in a UserRequest subclass
                    # results in a terminated job, not a zombie job
                    log.exception("Calling complete_jid for %s/%s" % (request.id, request.jid))
                    request.jid = None
                    request.set_error("Internal error %s" % e)
                    request.complete()

        if request.state == UserRequest.COMPLETE:
            self._manager.eventer.on_user_request_complete(request)

    def _update_index(self, request):
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
            old_jid = request.jid
            yield
            # Update by_jid in case this triggered a new job
            if request.jid != old_jid:
                if old_jid:
                    del self._by_jid[old_jid]
                if request.jid:
                    self._by_jid[request.jid] = request

        return update()
