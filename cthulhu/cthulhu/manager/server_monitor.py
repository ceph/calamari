
"""
While the cluster monitor pays attention to events about Ceph clusters (which
span non-disjoint sets of servers), the server monitor just pays attention to
individual hosts with no regard to the relations between them.
"""
from collections import defaultdict
import json
import datetime
from dateutil import tz
import logging

from gevent import greenlet
from gevent import event

from cthulhu.gevent_util import nosleep
from cthulhu.log import log as cthulhu_log
from cthulhu.manager import salt_config, config

# The type name for hosts and osds in the CRUSH map (if users have their
# own crush map they may have changed this), Ceph defaults are 'host' and 'osd'
from calamari_common.types import OsdMap, MonMap, ServiceId
from calamari_common.salt_wrapper import SaltEventSource, MasterPillarUtil
from cthulhu.util import now

CRUSH_HOST_TYPE = config.get('cthulhu', 'crush_host_type')
CRUSH_OSD_TYPE = config.get('cthulhu', 'crush_osd_type')

# Ignore changes in boot time below this threshold, to avoid mistaking clock
# adjustments for reboots.
REBOOT_THRESHOLD = datetime.timedelta(seconds=10)


# getChild isn't in 2.6
log = logging.getLogger('.'.join((cthulhu_log.name, 'server_monitor')))


class GrainsNotFound(Exception):
    pass


class ServerState(object):
    """
    A Ceph server, may be something we have had a heartbeat from or
    may be something we learned about from Ceph.
    """
    def __init__(self, fqdn, hostname, managed, last_contact, boot_time, ceph_version):
        # Note that FQDN is fudged when we learn about a server via
        # the CRUSH map (i.e. when we're talking to mons but not OSDs)
        # to contain the hostname instead.  The implied assumption
        # is that a system configured this way has unique hostnames.
        self.fqdn = fqdn
        self.hostname = hostname

        # Whether the server is managed by calamari (i.e. we are getting salt
        # telemetry) as opposed to inferred via Ceph mon data.
        self.managed = managed

        # Dict of ID tuple to ServiceState
        self.services = {}

        self.last_contact = last_contact
        self.boot_time = boot_time
        self.ceph_version = ceph_version

    @property
    def clusters(self):
        """
        Which clusters is this server involved with?

        return: A list of zero or more FSIDs
        """
        return list(set([service.fsid for service in self.services]))

    def __repr__(self):
        return "<ServerState '%s'>" % self.fqdn


class ServiceState(object):
    """
    A Ceph service, this object is used to track its affinity to a server
    """
    def __init__(self, fsid, service_type, service_id):
        # It's easy to accidentally pass in int sometimes so enforce consistency
        assert isinstance(service_id, basestring)

        self.fsid = fsid
        self.service_type = service_type
        self.service_id = service_id
        self.server_state = None

        # For services reported by managed servers, this is whether the
        # service is running.  For services reported by the Ceph mon, this
        # is whether Ceph believes the service to be in an 'up' state.
        self.running = True

        # For mons, we keep a copy of mon_status so that we can make sense
        # of situations where quorum is lost
        self.status = None

    @property
    def id(self):
        return ServiceId(self.fsid, self.service_type, self.service_id)

    def set_server(self, server_state):
        self.server_state = server_state

    def __repr__(self):
        return "<ServiceState '%s'>" % ((self.fsid, self.service_type, self.service_id),)


class ServerMonitor(greenlet.Greenlet):
    """
    This class receives updates about servers and their services from two sources:

    - The ceph.services salt message from managed servers
    - Updates to the OSD map which may tell us about unmanaged servers
    """
    def __init__(self, persister, eventer, requests):
        super(ServerMonitor, self).__init__()

        # FQDN to ServerState
        self.servers = {}

        # Hostname to ServerState
        self.hostname_to_server = {}

        # FSID to ServiceState list
        self.fsid_services = defaultdict(list)

        # Service (fsid, type, id) to ServiceState
        self.services = {}

        self._complete = event.Event()

        self._eventer = eventer
        self._persister = persister
        self._requests = requests

        # Cache things we look up from pillar to avoid hitting disk repeatedly
        self._contact_period_cache = {}

    def _run(self):
        log.info("Starting %s" % self.__class__.__name__)

        subscription = SaltEventSource(log, salt_config)

        while not self._complete.is_set():
            # No salt tag filtering: https://github.com/saltstack/salt/issues/11582
            ev = subscription.get_event(full=True)

            if ev is not None and ev['tag'].startswith("ceph/server"):
                data = ev['data']
                log.debug("ServerMonitor got ceph/server message from %s" % data['id'])
                try:
                    # NB assumption that FQDN==minion_id is true unless
                    # someone has modded their salt minion config.
                    self.on_server_heartbeat(data['id'], data['data'])
                except:
                    log.debug("Message detail: %s" % json.dumps(ev))
                    log.exception("Error handling ceph/server message from %s" % data['id'])
            if ev is not None and ev['tag'].startswith("salt/presen"):
                # so these exist but i'm not convinced they work, I started a minion
                # and then saw several messages indicating no mininions were present
                log.debug("ServerMonitor: presence %s" % ev['data'])

        log.info("Completed %s" % self.__class__.__name__)

    def get_contact_period(self, fqdn):
        """
        The reporting period depends on the pillar of the server (i.e. schedules.sls),
        so we look it up on a per-server basis.
        """
        try:
            return self._contact_period_cache[fqdn]
        except KeyError:
            result = self._contact_period_cache[fqdn] = self._get_contact_period(fqdn)
            return result

    def _get_contact_period(self, fqdn):
        pillar_util = MasterPillarUtil([fqdn], 'list',
                                       grains_fallback=False,
                                       pillar_fallback=False,
                                       opts=salt_config)

        try:
            heartbeat_s = pillar_util.get_minion_pillar()[fqdn]['schedule']['ceph.heartbeat']['seconds']
        except KeyError:
            # Just in case salt pillar is unavailable for some reason, a somewhat sensible
            # guess.  It's really an error, but I don't want to break the world in this case.
            fallback_contact_period = 60
            log.warn("Missing period in minion '{0}' pillar".format(fqdn))
            return fallback_contact_period

        return heartbeat_s

    def get_hostname_to_osds(self, osd_map):
        """
        Map 'hostname' to OSD: hostname in this context actually means
        CRUSH node name where node is of type 'host'.

        In a default Ceph deployment this will indeed be the hostname, but
        a logical server can have multiple CRUSH nodes with arbitrary names.
        """
        osd_tree = osd_map['tree']
        nodes_by_id = dict((n["id"], n) for n in osd_tree["nodes"])

        host_to_osd = defaultdict(list)

        osd_id_to_host = {}

        def find_descendants(cursor, fn):
            if fn(cursor):
                return [cursor]
            else:
                found = []
                for child_id in cursor['children']:
                    found.extend(find_descendants(nodes_by_id[child_id], fn))
                return found

        # This assumes that:
        # - The host and OSD types exist and have the names set
        #   in CRUSH_HOST_TYPE and CRUSH_OSD_TYPE
        # - That OSDs are descendents of hosts
        # - That hosts have the 'name' attribute set to their hostname
        # - That OSDs have the 'name' attribute set to osd.<osd id>
        # - That OSDs are not descendents of OSDs
        for node in osd_tree["nodes"]:
            if node["type"] == CRUSH_HOST_TYPE:
                host = node["name"]
                for osd in find_descendants(node, lambda c: c['type'] == CRUSH_OSD_TYPE):
                    osd_id_to_host[osd["id"]] = host

        for osd in osd_map['osds']:
            try:
                host_to_osd[osd_id_to_host[osd['osd']]].append(osd)
            except KeyError:
                # We didn't get the info we needed from CRUSH, do not include
                # this OSD in the output mapping.
                pass

        if len(host_to_osd) == 0:
            # A handy cue to debugging, in case CRUSH_[HOST|OSD]_TYPE are
            # set wrongly or somesuch
            log.debug("Warning: failed to process CRUSH host->osd mapping")

        return host_to_osd

    def inject_server(self, server_state):
        self.hostname_to_server[server_state.hostname] = server_state
        self.servers[server_state.fqdn] = server_state

    def inject_service(self, service_state, server_fqdn):
        server_state = self.servers[server_fqdn]
        self.services[service_state.id] = service_state
        service_state.set_server(server_state)
        server_state.services[service_state.id] = service_state
        self.fsid_services[service_state.fsid].append(service_state)

    def forget_service(self, service_state):
        log.info("Removing record of service %s" % (service_state,))
        self.fsid_services[service_state.fsid].remove(service_state)
        del self.services[service_state.id]
        if service_state.server_state:
            del service_state.server_state.services[service_state.id]
        self._persister.delete_service(service_state.id)

    @nosleep
    def on_osd_map(self, osd_map):
        """
        For when a new OSD map is received: we may infer the existence of
        hosts from the CRUSH map if the hosts are not all sending
        us data with salt.

        :param osd_map: The data from an OsdMap sync object
        """
        log.debug("ServerMonitor.on_osd_map: epoch %s" % osd_map['epoch'])

        hostname_to_osds = self.get_hostname_to_osds(osd_map)
        log.debug("ServerMonitor.on_osd_map: got service data for %s servers" % len(hostname_to_osds))

        osds_in_map = set()
        for hostname, osds in hostname_to_osds.items():
            id_to_osd = dict([(ServiceId(osd_map['fsid'], 'osd', str(o['osd'])), o) for o in osds])
            osds_in_map |= set(id_to_osd.keys())

            # Identify if this is a CRUSH alias rather than a real hostname, by
            # checking if any of the OSDs mentioned are already recorded as children
            # of a managed host.
            crush_alias_to = None
            if hostname not in self.hostname_to_server:
                for service_id, osd in id_to_osd.items():
                    try:
                        service_state = self.services[service_id]
                        if service_state.server_state.managed:
                            crush_alias_to = service_state.server_state
                    except KeyError:
                        pass

            if crush_alias_to:
                log.info("'{0}' is a CRUSH alias to {1}".format(hostname, crush_alias_to))
                continue

            # Look up or create ServerState for the server named in the CRUSH map
            try:
                server_state = self.hostname_to_server[hostname]
            except KeyError:
                # Fake FQDN to equal hostname
                server_state = ServerState(hostname, hostname, managed=False,
                                           last_contact=None, boot_time=None, ceph_version=None)
                self.inject_server(server_state)
                self._persister.create_server(
                    fqdn=server_state.fqdn,
                    hostname=server_state.hostname,
                    managed=server_state.managed)

            # Register all the OSDs reported under this hostname with the ServerState
            for service_id, osd in id_to_osd.items():
                if not server_state.managed:
                    # Only pay attention to these services for unmanaged servers,
                    # for managed servers rely on ceph/server salt messages
                    self._register_service(server_state, service_id, bool(osd['up']), None)

        # Remove ServiceState for any OSDs for this FSID which are not
        # mentioned in hostname_to_osds
        known_osds = set([s.id for s in self.fsid_services[osd_map['fsid']] if s.service_type == 'osd'])
        for stale_service_id in known_osds - osds_in_map:
            self.forget_service(self.services[stale_service_id])

    @nosleep
    def on_mds_map(self, fsid, mds_map):
        """
        When a new MDS map is received, use it to eliminate any MDS
        ServiceState records that no longer exist in the real world.

        :param fsid: Pass in fsid string because mds map doesn't include it
        :param mds_map: The MDS map sync object
        """
        map_mds = set([ServiceId(
            fsid, 'mds', i['name']
        ) for i in mds_map['info'].values()])
        known_mds = set([s.id for s in self.fsid_services[fsid] if s.service_type == 'mds'])
        for stale_mds_id in known_mds - map_mds:
            self.forget_service(self.services[stale_mds_id])

    @nosleep
    def on_mon_map(self, mon_map):
        """
        When a new mon map is received, use it to eliminate any mon
        ServiceState records that no longer exist in the real world.
        """
        map_mons = set([ServiceId(mon_map['fsid'], 'mon', m['name']) for m in mon_map['mons']])
        known_mons = set([
            s.id
            for s in self.fsid_services[mon_map['fsid']] if s.service_type == 'mon'
        ])
        for stale_mon_id in known_mons - map_mons:
            self.forget_service(self.services[stale_mon_id])

    def _get_grains(self, fqdn):
        pillar_util = MasterPillarUtil(fqdn, 'glob',
                                       use_cached_grains=True,
                                       grains_fallback=False,
                                       opts=salt_config)
        try:
            return pillar_util.get_minion_grains()[fqdn]
        except KeyError:
            raise GrainsNotFound(fqdn)

    @nosleep
    def on_server_heartbeat(self, fqdn, server_heartbeat):
        """
        Call back for when a ceph.service message is received from a salt minion.

        This is actually a fairly simple operation of updating the in memory ServerState
        to reflect what is in the message, but it's convoluted because we may be seeing
        a new server, a known server, or a server which was known but unmanaged.
        """
        log.debug("ServerMonitor.on_server_heartbeat: %s" % fqdn)
        new_server = True
        newly_managed_server = False
        try:
            server_state = self.servers[fqdn]
            new_server = False
        except KeyError:
            # Look up the grains for this server, we need to know its hostname in order
            # to resolve this vs. the OSD map.
            hostname = self._get_grains(fqdn)['host']

            if hostname in self.hostname_to_server:
                server_state = self.hostname_to_server[hostname]
                if not server_state.managed:
                    # Take over a ServerState that was created from OSD map
                    server_state.managed = True
                    old_fqdn = server_state.fqdn
                    # OSD map servers would have faked up FQDN as hostname, so clear that out
                    del self.servers[old_fqdn]
                    server_state.fqdn = fqdn
                    self.servers[server_state.fqdn] = server_state
                    self._persister.update_server(old_fqdn, fqdn=fqdn, managed=True)
                    new_server = False
                    log.info("Server %s went from unmanaged to managed" % fqdn)
                    newly_managed_server = True
                else:
                    # We will go on to treat these as distinct servers even though
                    # they have the same hostname
                    log.warn("Hostname clash: FQDNs '%s' and '%s' both have hostname %s" % (
                        fqdn, server_state.fqdn, hostname
                    ))
        else:
            # The case where hostname == FQDN, we may already have this FQDN in our
            # map from an unmanaged server being reported by hostname.
            if not server_state.managed:
                newly_managed_server = True
                server_state.managed = True
                self._persister.update_server(server_state.fqdn, managed=True)
                log.info("Server %s went from unmanaged to managed" % fqdn)

        boot_time = datetime.datetime.fromtimestamp(server_heartbeat['boot_time'], tz=tz.tzutc())
        if new_server:
            hostname = self._get_grains(fqdn)['host']
            server_state = ServerState(fqdn, hostname, managed=True,
                                       last_contact=now(), boot_time=boot_time,
                                       ceph_version=server_heartbeat['ceph_version'])
            self.inject_server(server_state)
            self._persister.create_server(
                fqdn=server_state.fqdn,
                hostname=server_state.hostname,
                managed=server_state.managed,
                last_contact=server_state.last_contact
            )
            log.info("Saw server %s for the first time" % server_state)

        server_state.last_contact = now()
        self._persister.update_server(server_state.fqdn, last_contact=server_state.last_contact)

        if server_state.boot_time != boot_time:
            log.warn("{0} boot time changed, old {1} new {2}".format(
                server_state.fqdn, server_state.boot_time, boot_time
            ))
            old_boot_time = server_state.boot_time
            server_state.boot_time = boot_time
            self._persister.update_server(server_state.fqdn, boot_time=server_state.boot_time)
            if old_boot_time is not None:  # i.e. a reboot, not an unmanaged->managed transition
                if server_state.boot_time < old_boot_time:
                    log.warn("Server boot time went backwards")
                elif server_state.boot_time - old_boot_time < REBOOT_THRESHOLD:
                    log.warn("Server boot time changed, but only a little")
                else:
                    # A substantial forward change in boot time, that's a reboot: emit
                    # a user visible event
                    log.warn("{0} rebooted!".format(fqdn))
                    self._eventer.on_reboot(server_state, False)

        if server_state.ceph_version != server_heartbeat['ceph_version']:
            # Interpret "no package installed but some services running" as meaning we're
            # in the process of upgrading.
            upgrading = server_heartbeat['ceph_version'] is None and server_heartbeat['services']
            if server_heartbeat['ceph_version'] is None and upgrading:
                # Ignore version=None while upgrading to avoid generating spurious
                # "ceph uninstalled" events
                pass
            else:
                server_state.ceph_version = server_heartbeat['ceph_version']
                self._persister.update_server(server_state.fqdn, ceph_version=server_state.ceph_version)
                if not (new_server or newly_managed_server):
                    self._eventer.on_new_version(server_state)

        seen_id_tuples = set()
        for service_name, service in server_heartbeat['services'].items():
            id_tuple = ServiceId(service['fsid'], service['type'], service['id'])
            seen_id_tuples.add(id_tuple)
            self._register_service(server_state, id_tuple, running=True, status=service['status'])

        # For any service which was last reported on this server but
        # is now gone, mark it as not running
        for unseen_id_tuple in set(server_state.services.keys()) ^ seen_id_tuples:
            service_state = self.services[unseen_id_tuple]
            if service_state.running:
                log.info("Service %s stopped on server %s" % (service_state, server_state))
                service_state.running = False

        if new_server or newly_managed_server:
            # We do this at the end so that by the time we emit the event
            # the ServiceState objects have been created
            self._eventer.on_server(server_state)

    def _register_service(self, server_state, service_id, running, status):
        log.debug("ServerMonitor._register_service: %s" % (service_id,))
        try:
            service_state = self.services[service_id]
        except KeyError:
            log.info("Saw service %s for the first time" % (service_id,))
            service_state = ServiceState(*service_id)
            self.inject_service(service_state, server_state.fqdn)

            self._persister.create_service(server_state.fqdn,
                                           fsid=service_state.fsid,
                                           service_type=service_state.service_type,
                                           service_id=service_state.service_id,
                                           status=json.dumps(status))

        if running != service_state.running:
            if running:
                log.info("Service %s started" % service_state)
                service_state.running = True
            else:
                log.info("Service %s stopped" % service_state)
                service_state.running = False

            self._persister.update_service(service_state.id, running=service_state.running)

        if status != service_state.status:
            # This usually means the mon status object has changed, we'll get one
            # of these from each up mon every time the mon cluster state changes.
            log.info("Service %s status update" % service_state)
            service_state.status = status
            self._persister.update_service(service_state.id, status=json.dumps(service_state.status))

        if service_state.server_state != server_state:
            old_server_state = service_state.server_state
            log.info("Associated service %s with server %s (was %s)" % (service_id, server_state, old_server_state))
            service_state.set_server(server_state)
            if old_server_state is not None:
                del old_server_state.services[service_id]
            server_state.services[service_id] = service_state
            self._persister.update_service_location(service_state.id, service_state.server_state.fqdn)

            if old_server_state.managed is False and not old_server_state.services:
                log.info("Expunging stale server record {0}".format(old_server_state.fqdn))
                del self.servers[old_server_state.fqdn]
                self._persister.delete_server(old_server_state.fqdn)

    def stop(self):
        self._complete.set()

    def get_all_cluster(self, fsid):
        """
        All the ServerStates which are involved in
        this cluster (i.e. hosting a service with this FSID)
        """
        return list(set([s.server_state for s in self.fsid_services[fsid] if s.server_state is not None]))

    def get_all(self):
        """Give me all the ServerStates"""
        return self.servers.values()

    def get_one(self, fqdn):
        """
        Give me a single ServerState, looked up by FQDN.
        """
        return self.servers[fqdn]

    def get_by_service(self, service_id):
        """
        Return the FQDN of the server associated with this service, or
        None if the service isn't found or isn't associated with a server.
        """
        try:
            return self.services[service_id].server_state
        except KeyError:
            log.warn("No server found for service %s" % (service_id,))
            return None

    def list_by_service(self, service_ids):
        """
        Return a list of 2-tuples mapping service ID to FQDN for the specified services,
        where the FQDN is None if service not found.
        """
        result = []
        for service_id in service_ids:
            server = self.get_by_service(service_id)
            result.append((service_id, server.fqdn if server else None))
        return result

    def get_services(self, service_ids):
        """
        Look up a list of ServiceState objects by ID.

        :param service_ids: A list of ServiceId
        :returns: A list of the same length as service_ids, containing ServiceState
                objects or None for any unfound ServiceIds.
        """
        return [self.services.get(service_id, None) for service_id in service_ids]

    def delete(self, fqdn):
        """
        Forget about this server.  Does not prevent it popping back into
        existence if we see reference to it in an incoming event.
        """
        server_state = self.servers[fqdn]
        for service in server_state.services.values():
            service.server_state = None
            del self.services[service.id]
            self.fsid_services[service.id.fsid].remove(service)
            self._persister.delete_service(service.id)

        if server_state.hostname in self.hostname_to_server:
            # This isn't always the case, because if two server had the same hostname
            # and one was deleted, the second one is not present in hostname_to_server any more
            del self.hostname_to_server[server_state.hostname]
        del self.servers[fqdn]
        self._persister.delete_server(fqdn)

    def delete_cluster(self, fsid):
        if fsid not in self.fsid_services:
            log.info("delete_cluster: No services for FSID %s" % fsid)
            return

        for service in self.fsid_services[fsid]:
            del self.services[service.id]
            if service.server_state:
                del service.server_state.services[service.id]
            self._persister.delete_service(service.id)

            # If we inferred a host from the OSD map for this cluster
            # then when the last service is gone the server should
            # go away too
            if service.server_state and (not service.server_state.managed) and (not service.server_state.services):
                self.delete(service.server_state.fqdn)

        del self.fsid_services[fsid]

    def dump(self, server_state):
        """
        Convert a ServerState into a serializable format
        """
        return {
            'fqdn': server_state.fqdn,
            'hostname': server_state.hostname,
            'managed': server_state.managed,
            'last_contact': server_state.last_contact.isoformat() if server_state.last_contact else None,
            'boot_time': server_state.boot_time.isoformat() if server_state.boot_time else None,
            'ceph_version': server_state.ceph_version,
            'services': [{'id': tuple(s.id), 'running': s.running} for s in server_state.services.values()]
        }

    def dump_cluster(self, server_state, cluster):
        """
        Convert a ServerState into a serializable format, including contextual
        information for the server's membership in a particular cluster.

        :param server_state: The ServerState to be dumped
        :param cluster: ClusterMonitor context
        """

        services = [s for s in server_state.services.values() if s.fsid == cluster.fsid]

        frontend_addr = None
        backend_addr = None

        for service in services:
            if frontend_addr is None and service.service_type == 'mon':
                # Go find the mon in the monmap and tell me its addr
                mon_map = cluster.get_sync_object_data(MonMap)
                if mon_map is not None:
                    mon = [mon for mon in mon_map['mons'] if mon['name'] == service.service_id][0]
                    frontend_addr = mon['addr'].split(":")[0]

            if (frontend_addr is None or backend_addr is None) and service.service_type == 'osd':
                # Go find the OSD in the OSD map and tell me its frontend and backend addrs
                osd_map = cluster.get_sync_object_data(OsdMap)
                if osd_map is not None:
                    osd = [osd for osd in osd_map['osds'] if str(osd['osd']) == service.service_id]
                    # osd can be empty at this point if the OSD is DNE (it's
                    # in server_state.services, but not in the osd_map)
                    if len(osd) > 0:
                        osd = osd[0]
                        frontend_addr = osd['public_addr'].split(":")[0]
                        backend_addr = osd['cluster_addr'].split(":")[0]

        return {
            'fqdn': server_state.fqdn,
            'hostname': server_state.hostname,
            'managed': server_state.managed,
            'last_contact': server_state.last_contact.isoformat() if server_state.last_contact else None,
            'boot_time': server_state.boot_time.isoformat() if server_state.boot_time else None,
            'ceph_version': server_state.ceph_version,
            'services': [{'id': tuple(s.id), 'running': s.running} for s in services],
            'frontend_addr': frontend_addr,
            'backend_addr': backend_addr
        }
