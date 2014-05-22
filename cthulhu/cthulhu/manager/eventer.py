from collections import defaultdict
import datetime

import gevent.event
import gevent.greenlet

from cthulhu.gevent_util import nosleep
from cthulhu.log import log
from calamari_common.types import OsdMap, Health, MonStatus, ServiceId, MON, OSD, MDS, INFO, severity_str, WARNING, \
    RECOVERY, ERROR
from cthulhu.manager import config
from cthulhu.util import now


# The tick handler is very cheap (no I/O) so we call
# it quite frequently.
TICK_SECONDS = 10

# The time-based checks don't kick in until after
# a grace period, to avoid generating complaints
# about "stale" timestamps immediately after startup
GRACE_PERIOD = 30

# How long must a [server|cluster] be out of contact before
# we generate an event?
CONTACT_THRESHOLD_FACTOR = int(config.get('cthulhu', 'server_timeout_factor'))  # multiple of contact period
CLUSTER_CONTACT_THRESHOLD = int(config.get('cthulhu', 'cluster_contact_threshold'))  # in seconds


class Event(object):
    def __init__(self, severity, message, **associations):
        self.severity = severity
        self.message = message
        self.associations = associations
        self.when = now()


class Eventer(gevent.greenlet.Greenlet):
    """
    I listen to changes from ClusterMonitor and ServerMonitor, and feed
    events into the event log.  I also periodically check some time-based
    conditions in my on_tick method.
    """

    def __init__(self, manager):
        super(Eventer, self).__init__()
        self._manager = manager

        self._complete = gevent.event.Event()

        # Flags for things we have complained about being out of contact
        # with, to avoid generating the same events repeatedly
        self._servers_complained = set()
        self._clusters_complained = set()

        self._events = []

    def stop(self):
        log.debug("Eventer stopping")
        self._complete.set()

    def _run(self):
        self._emit(INFO, "Calamari server started")
        self._flush()

        self._complete.wait(GRACE_PERIOD)
        while not self._complete.is_set():
            self.on_tick()
            self._complete.wait(TICK_SECONDS)
        log.debug("Eventer complete")

    def _emit(self, severity, message, **associations):
        """
        :param severity: One of the defined serverity values
        :param message: One line human readable string
        :param associations: Optional extra attributes to associate
                             the event with a particular cluster/server/service
        """
        log.info("Eventer._emit: %s/%s" % (severity_str(severity), message))

        self._events.append(Event(severity, message, **associations))

    def on_user_request_begin(self, request):
        self._emit(INFO, "Started: %s" % request.headline, **request.associations)
        self._flush()

    def on_user_request_complete(self, request):
        if request.error:
            self._emit(WARNING, "Failed: {headline} ({error})".format(
                headline=request.headline, error=request.error_message), **request.associations)
        else:
            self._emit(INFO, "Succeeded: %s" % request.headline, **request.associations)
        self._flush()

    def _flush(self):
        if self._events:
            self._manager.persister.save_events(self._events)
            self._events = []

    # TODO consume messages about ServiceState from ServerMonitor, so that
    # we can tell people about their services in the absence of up to date
    # cluster map information.

    def _humanize_service(self, service_count, service_type):
        """
        String helper for printing strings like "1 OSD", "2 MDSs"
        """
        human_singular = {
            MON: 'monitor service',
            OSD: 'OSD',
            MDS: 'MDS'
        }
        return "{count} {human_service}{pluralize}".format(
            count=service_count,
            human_service=human_singular[service_type],
            pluralize="s" if service_count > 1 else ""
        )

    def _server_fsid(self, server_state):
        # If the server has only services for exactly one FSID, then we
        # can associate the event with the FSID.
        fsids = set([s.fsid for s in server_state.services])
        if len(fsids) == 1:
            fsid = fsids.pop()
        else:
            fsid = None

        return fsid

    @nosleep
    def on_server(self, server_state):
        """
        Tell me that a new (managed) server has appeared in our world.
        """
        msg = "Added server %s" % server_state.fqdn
        counts_by_type = defaultdict(int)
        for service in server_state.services:
            counts_by_type[service.service_type] += 1
        if counts_by_type:
            msg += " with "
            msg += ", ".join([
                self._humanize_service(count, service_type)
                for (service_type, count) in counts_by_type.items()])

        self._emit(INFO, msg, fqdn=server_state.fqdn, fsid=self._server_fsid(server_state))

    @nosleep
    def on_reboot(self, server_state, expected):
        """
        Tell me that a server rebooted.

        :param expected: True if the server was in a rebooting state already (i.e.
                         we told it to reboot).  False indicates spontaneity)
        """
        severity = INFO if expected else WARNING
        self._emit(severity,
                   "Server {fqdn} rebooted".format(fqdn=server_state.fqdn),
                   fqdn=server_state.fqdn,
                   fsid=self._server_fsid(server_state))

    @nosleep
    def on_new_version(self, server_state):
        """
        Tell me that the version of ceph changed
        """
        if server_state.ceph_version is not None:
            msg = "Ceph {version} installed on {fqdn}".format(
                fqdn=server_state.fqdn, version=server_state.ceph_version)
        else:
            msg = "Ceph uninstalled from {fqdn}".format(fqdn=server_state.fqdn)

        self._emit(INFO, msg,
                   fqdn=server_state.fqdn,
                   fsid=self._server_fsid(server_state))

    @nosleep
    def on_tick(self):
        """
        Periodically call this to drive non-event-driven events (i.e. things
        which are based on walltime checks)
        """
        log.debug("Eventer.on_tick")

        now_utc = now()

        for fqdn, server_state in self._manager.servers.servers.items():
            if not server_state.managed:
                # We don't expect messages from unmanaged servers so don't
                # worry about whether they sent us one recently.
                continue

            if len(server_state.clusters) == 1:
                # Because Events can only be associated with one FSID, we only make this
                # association for servers with exactly one cluster.  This is a bit cheeky and
                # kind of an unnecessary limitation in the Event DB schema.
                fsid = server_state.clusters[0]
            else:
                fsid = None

            contact_threshold = CONTACT_THRESHOLD_FACTOR * self._manager.servers.get_contact_period(fqdn)
            if now_utc - server_state.last_contact > datetime.timedelta(seconds=contact_threshold):
                if fqdn not in self._servers_complained:
                    self._emit(WARNING, "Server {fqdn} is late reporting in, last report at {last}".format(
                        fqdn=fqdn, last=server_state.last_contact
                    ), fqdn=fqdn, fsid=fsid)
                    self._servers_complained.add(fqdn)
            else:
                if fqdn in self._servers_complained:
                    self._emit(RECOVERY, "Server {fqdn} regained contact".format(fqdn=fqdn),
                               fqdn=fqdn, fsid=fsid)
                    self._servers_complained.discard(fqdn)

        for fsid, cluster_monitor in self._manager.clusters.items():
            if cluster_monitor.update_time is None or now_utc - cluster_monitor.update_time > datetime.timedelta(
                    seconds=CLUSTER_CONTACT_THRESHOLD):
                if fsid not in self._clusters_complained:
                    self._clusters_complained.add(fsid)
                    self._emit(WARNING, "Cluster '{name}' is late reporting in".format(name=cluster_monitor.name),
                               fsid=fsid)
            else:
                if fsid in self._clusters_complained:
                    self._emit(RECOVERY, "Cluster '{name}' regained contact".format(name=cluster_monitor.name),
                               fsid=fsid)
                    self._clusters_complained.discard(fsid)

        self._flush()

    def _get_fqdn(self, fsid, service_type, service_id):
        """
        Resolve a service to a FQDN if possible, else return None
        """
        server = self._manager.servers.get_by_service(ServiceId(fsid, service_type, str(service_id)))
        if server is None:
            log.warn("No server found for service %s %s" % (service_type, service_id))
        return server.fqdn if server else None

    def _get_on_server(self, fsid, service_type, service_id):
        """
        Get a string for appending to service messages to indicate
        which server they're on, or "" if none.
        """
        fqdn = self._get_fqdn(fsid, service_type, service_id)
        if fqdn:
            return " (on %s)" % fqdn
        else:
            return ""

    def _on_osd_map(self, fsid, new, old):
        old_osd_ids = set([o['osd'] for o in old.data['osds']])
        new_osd_ids = set([o['osd'] for o in new.data['osds']])
        deleted_osds = old_osd_ids - new_osd_ids
        created_osds = new_osd_ids - old_osd_ids

        def osd_event(severity, msg, osd_id):
            self._emit(
                severity,
                msg.format(
                    name=self._manager.clusters[fsid].name,
                    id=osd_id,
                    on_server=self._get_on_server(fsid, 'osd', osd_id)
                ),
                fsid=fsid,
                fqdn=self._get_fqdn(fsid, 'osd', osd_id),
                service_type='osd',
                service_id=str(osd_id))

        # Generate events for removed OSDs
        for osd_id in deleted_osds:
            osd_event(INFO, "OSD {name}.{id}{on_server} removed from the cluster map", osd_id)

        # Generate events for added OSDs
        for osd_id in created_osds:
            osd_event(INFO, "OSD {name}.{id}{on_server} added to the cluster map", osd_id)

        # Generate events for changed OSDs
        for osd_id in old_osd_ids & new_osd_ids:
            old_osd = old.osds_by_id[osd_id]
            new_osd = new.osds_by_id[osd_id]
            if old_osd['up'] != new_osd['up']:
                if bool(new_osd['up']):
                    osd_event(RECOVERY, "OSD {name}.{id} came up{on_server}", osd_id)
                else:
                    osd_event(WARNING, "OSD {name}.{id} went down{on_server}", osd_id)

                    # TODO: aggregate OSD notifications by server so that we can say things
                    # like "all the OSDs on server X went down" or "2/3 OSDs on server X went down"
                    # TODO: aggregate OSD notifications by cluster so that we can say "all OSDs
                    # in cluster 'foo' are down"

                    # TODO Generate notifications if all the OSDs on a server are 'down',
                    # the downness OSD map is more recent than the last contact
                    # with the server, and we haven't already reported the server laggy,
                    # to indicate that our best guess here is that the server itself is down.

    def _on_mon_status(self, fsid, new, old):
        old_quorum = set(old.data['quorum'])
        new_quorum = set(new.data['quorum'])

        def _mon_event(severity, msg, mon_rank):
            name = new.mons_by_rank[mon_rank]['name']
            self._emit(severity,
                       msg.format(
                           cluster_name=self._manager.clusters[fsid].name,
                           mon_name=name,
                           on_server=self._get_on_server(fsid, 'mon', name)),
                       fsid=fsid,
                       fqdn=self._get_fqdn(fsid, 'mon', name))

        for rank in new_quorum - old_quorum:
            _mon_event(RECOVERY, "Mon '{cluster_name}.{mon_name}' joined quorum{on_server}", rank)

        for rank in old_quorum - new_quorum:
            _mon_event(WARNING, "Mon '{cluster_name}.{mon_name}' left quorum{on_server}", rank)

    def _on_health(self, fsid, new, old):
        # Generate notifications for transitions between HEALTH_OK, HEALTH_WARN, HEALTH_ERR
        old_status = old.data['overall_status']
        new_status = new.data['overall_status']
        health_severity = {
            "HEALTH_OK": INFO,
            "HEALTH_WARN": WARNING,
            "HEALTH_ERR": ERROR
        }

        if old_status != new_status:
            if health_severity[new_status] < health_severity[old_status]:
                # A worsening of health
                event_sev = health_severity[new_status]
                msg = "Health of cluster '{name}' degraded from {old} to {new}".format(
                    old=old_status, new=new_status, name=self._manager.clusters[fsid].name)
            else:
                # An improvement in health
                event_sev = RECOVERY
                msg = "Health of cluster '{name}' recovered from {old} to {new}".format(
                    old=old_status, new=new_status, name=self._manager.clusters[fsid].name)

            if health_severity[new_status] < INFO:
                # XXX I'm not sure how much I like this, it puts data on the screen
                # which will soon be stale
                pass
                # msg += " (%s)" % (new.data['summary'][0]['summary'])
            self._emit(event_sev, msg, fsid=fsid)

    @nosleep
    def on_sync_object(self, fsid, sync_type, new, old):
        """
        Notification that a newer version of a SyncObject is available, or
        the first version of a SyncObject is available at startup (wherein
        old will be a null SyncObject)

        :param fsid: The FSID of the cluster to which the object belongs
        :param sync_type: A SyncObject subclass
        :param new: A SyncObject
        :param old: A SyncObject (same type as new)
        """
        log.debug("Eventer.on_sync_object: %s" % sync_type.str)

        if old.data is None:
            return

        if sync_type == OsdMap:
            self._on_osd_map(fsid, new, old)
        elif sync_type == Health:
            self._on_health(fsid, new, old)
        elif sync_type == MonStatus:
            self._on_mon_status(fsid, new, old)

        self._flush()

        # TODO: generate notifications on PG map to indicate anything particularly
        # interesting like things which are in a bad state and won't be recovering
        # TODO: generate events from MDS map
