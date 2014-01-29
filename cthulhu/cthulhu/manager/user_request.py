import uuid
import salt
import salt.client
from salt.client import LocalClient
from cthulhu.manager import config
from cthulhu.log import log
from cthulhu.manager.types import OsdMap, PgBrief, USER_REQUEST_COMPLETE, USER_REQUEST_SUBMITTED
from cthulhu.util import now


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
    of their remote ID (salt jid).  UserRequests may also execute more than
    one JID in the course of their lifetime.

    Requests have the following lifecycle:
     NEW object is created, it has all the information needed to do its job
         other than where it should execute.
     SUBMITTED the request has started executing, usually this will have involved sending
               out a salt job, so .jid is often set but not always.
     COMPLETE no further action, this instance will remain constant from this point on.
              this does not indicate anything about success or failure.
    """

    NEW = 'new'
    SUBMITTED = USER_REQUEST_SUBMITTED
    COMPLETE = USER_REQUEST_COMPLETE
    states = [NEW, SUBMITTED, COMPLETE]

    def __init__(self, fsid, cluster_name, commands):
        """
        Requiring cluster_name and fsid is redundant (ideally everything would
        speak in terms of fsid) but convenient, because the librados interface
        wants a cluster name when you create a client, and otherwise we would
        have to look up via ceph.conf.
        """
        self.log = log.getChild(self.__class__.__name__)

        self.requested_at = now()
        self.completed_at = None

        # This is actually kind of overkill compared with having a counter,
        # somewhere but it's easy.
        self.id = uuid.uuid4().__str__()

        self._minion_id = None
        self._fsid = fsid
        self._cluster_name = cluster_name
        self._commands = commands

        self.jid = None

        self.state = self.NEW
        self.result = None
        self.error = False
        self.error_message = ""

        # Time at which we last believed the current JID to be really running
        self.alive_at = None

    def set_error(self, message):
        self.error = True
        self.error_message = message

    @property
    def minion_id(self):
        return self._minion_id

    @property
    def associations(self):
        """
        A dictionary of Event-compatible assocations for this request, indicating
        which cluster/server/services we are affecting.
        """
        return {}

    @property
    def headline(self):
        """
        Single line describing what the request is trying to accomplish.
        """
        raise NotImplementedError()

    @property
    def status(self):
        """
        Single line describing which phase of the request is currently happening, useful
        to distinguish what's going on for long running operations.  For simple quick
        operations no need to return anything here as the headline tells all.
        """
        if self.state != self.COMPLETE:
            return "Running"
        elif self.error:
            return "Failed (%s)" % self.error_message
        else:
            return "Completed successfully"

    @property
    def awaiting_versions(self):
        """
        Jobs may advertise that they are waiting for particular versions,
        so that ClusterMonitor can be encouraged to fetch those

        :return dict of SyncObject subclass to version
        """
        return {}

    def submit(self, minion_id):
        """
        Start remote execution phase by publishing a job to salt.
        """
        assert self.state == self.NEW

        self._minion_id = minion_id
        self._submit(self._commands)

        self.state = self.SUBMITTED

    def _submit(self, commands):
        self.log.debug("Request._submit: %s/%s/%s" % (self._minion_id, self._cluster_name, commands))

        client = LocalClient(config.get('cthulhu', 'salt_config_path'))
        pub_data = client.run_job(self._minion_id, 'ceph.rados_commands',
                                  [self._fsid, self._cluster_name, commands])
        if not pub_data:
            # FIXME: LocalClient uses 'print' to record the
            # details of what went wrong :-(
            raise PublishError("Failed to publish job")

        self.log.info("Request %s started job %s" % (self.id, pub_data['jid']))

        self.alive_at = now()
        self.jid = pub_data['jid']

        return self.jid

    def complete_jid(self, result):
        """
        Call this when remote execution is done.

        Implementations must always update .jid appropriately here: either to the
        jid of a new job, or to None.
        """
        self.result = result
        self.log.info("Request %s JID %s completed with result=%s" % (self.id, self.jid, self.result))
        self.jid = None

        # This is a default behaviour for UserRequests which don't override this method:
        # assume completion of a JID means the job is now done.
        self.complete()

    def complete(self):
        """
        Call this when you're all done
        """
        self.log.info("Request %s completed with error=%s (%s)" % (self.id, self.error, self.error_message))
        self.state = self.COMPLETE
        self.completed_at = now()

    def on_map(self, sync_type, sync_objects):
        pass


class OsdMapModifyingRequest(UserRequest):
    """
    Specialization of UserRequest which waits for Calamari's copy of
    the OsdMap sync object to catch up after execution of RADOS commands.
    """

    def __init__(self, headline, fsid, cluster_name, commands):
        super(OsdMapModifyingRequest, self).__init__(fsid, cluster_name, commands)
        self._await_version = None
        self._headline = headline

    @property
    def headline(self):
        return self._headline

    @property
    def status(self):
        if self._await_version:
            return "Waiting for OSD map epoch %s" % self._await_version
        elif not self.state != self.COMPLETE:
            return "Running remote commands"
        else:
            return super(OsdMapModifyingRequest, self).status

    @property
    def associations(self):
        return {
            'fsid': self._fsid
        }

    @property
    def awaiting_versions(self):
        if self._await_version and self.state != self.COMPLETE:
            return {
                OsdMap: self._await_version
            }
        else:
            return None

    def complete_jid(self, result):
        # My remote work is done, record the version of the map that I will wait for
        # and start waiting for it.
        self.jid = None
        self.result = result
        self._await_version = result['versions']['osd_map']

    def on_map(self, sync_type, sync_objects):
        if sync_type != OsdMap:
            return

        osd_map = sync_objects.get(OsdMap)
        ready = osd_map.version >= self._await_version
        if ready:
            self.log.debug("check passed (%s >= %s)" % (osd_map.version, self._await_version))
            self.complete()
        else:
            self.log.debug("check pending (%s < %s)" % (osd_map.version, self._await_version))


class PgCreatingRequest(OsdMapModifyingRequest):
    """
    Specialization of OsdMapModifyingRequest to issue a request
    to issue a second set of commands after PGs created by an
    initial set of commands have left the 'creating' state.
    """
    PRE_CREATE = 'pre_create'
    CREATING = 'creating'
    POST_CREATE = 'post_create'

    def __init__(self, headline, fsid, cluster_name, commands, post_create_commands, pool_id, pg_count):
        super(PgCreatingRequest, self).__init__(headline, fsid, cluster_name, commands)
        self._post_create_commands = post_create_commands

        self._phase = self.PRE_CREATE
        self._await_osd_version = None

        self._pool_id = pool_id
        self._pg_count = pg_count

        self._headline = headline

    @property
    def status(self):
        if self._phase == self.CREATING:
            return "Waiting for PGs to be created"
        else:
            return super(PgCreatingRequest, self).status

    def complete_jid(self, result):
        if self._phase == self.PRE_CREATE:
            # The initial tranche of jobs has completed, start waiting
            # for PG creation to complete
            self.jid = None
            self._await_osd_version = result['versions']['osd_map']
            self._phase = self.CREATING
            self.log.debug("PgCreatingRequest PRE_CREATE->CREATING")
        elif self._phase == self.POST_CREATE:
            # Act just like an OSD map modification
            super(PgCreatingRequest, self).complete_jid(result)

    def on_map(self, sync_type, sync_objects):
        self.log.debug("PgCreatingRequest %s %s" % (sync_type.str, self._phase))
        if self._phase == self.PRE_CREATE:
            return
        elif self._phase == self.CREATING:
            if sync_type == PgBrief:
                # Count the PGs in this pool which are not in state 'creating'
                pgs = sync_objects.get(PgBrief).data
                pg_counter = 0
                for pg in pgs:
                    pg_pool_id = int(pg['pgid'].split(".")[0])
                    self.log.debug("PgCreatingRequest %s %s %s %s" % (
                        pg['pgid'], pg_pool_id, self._pool_id, pg['state']
                    ))
                    if pg_pool_id != self._pool_id:
                        continue
                    else:
                        states = pg['state'].split("+")
                        if 'creating' not in states:
                            pg_counter += 1

                self.log.debug("PgCreatingRequest.on_map: pg_counter=%s/%s" % (pg_counter, self._pg_count))
                if pg_counter >= self._pg_count:
                    self._phase = self.POST_CREATE
                    self.log.debug("PgCreatingRequest CREATING->POST_CREATE")
                    self._submit(self._post_create_commands)
        elif self._phase == self.POST_CREATE:
            super(PgCreatingRequest, self).on_map(sync_type, sync_objects)
