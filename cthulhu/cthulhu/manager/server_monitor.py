
"""
While the cluster monitor pays attention to events about Ceph clusters (which
span non-disjoint sets of servers), the server monitor just pays attention to
individual hosts with no regard to the relations between them.
"""
from collections import defaultdict, namedtuple
import json
import datetime
from dateutil import tz

from gevent import greenlet
from gevent import event
import salt.utils.event
import salt.utils.master
from cthulhu.gevent_util import nosleep

from cthulhu.log import log
from cthulhu.manager import salt_config, config

# The type name for hosts and osds in the CRUSH map (if users have their
# own crush map they may have changed this), Ceph defaults are 'host' and 'osd'
from cthulhu.manager.types import OsdMap, MonMap
from cthulhu.persistence.servers import Server, Service

CRUSH_HOST_TYPE = config.get('cthulhu', 'crush_host_type')
CRUSH_OSD_TYPE = config.get('cthulhu', 'crush_osd_type')

# Stuff still to do:
# - (maybe) report ceph version in ceph.services
# - (maybe) add a sanity check of the mons known to ServerMonitor vs those known in
#   mon map: loudly complain if there's anybody in the mon map who isn't on a managed
#   server in ServerMonitor.  Could just be to log to begin with, later hook into event
#   generation.


def now():
    """
    A tz-aware now
    """
    return datetime.datetime.utcnow().replace(tzinfo=tz.tzutc())


class GrainsNotFound(Exception):
    pass


class ServerState(object):
    """
    A Ceph server, may be something we have had a heartbeat from or
    may be something we learned about from Ceph.
    """
    def __init__(self, fqdn, hostname, managed, last_contact):
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

    def __repr__(self):
        return "<ServerState '%s'>" % self.fqdn


ServiceId = namedtuple('ServiceId', ['fsid', 'service_type', 'service_id'])


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
    def __init__(self, persister):
        super(ServerMonitor, self).__init__()

        self._persister = persister

        # FQDN to ServerState
        self.servers = {}

        # Hostname to ServerState
        self.hostname_to_server = {}

        # FSID to ServiceState list
        self.fsid_services = defaultdict(list)

        # Service (fsid, type, id) to ServiceState
        self.services = {}

        self._complete = event.Event()

    def _run(self):
        log.info("Starting %s" % self.__class__.__name__)
        subscription = salt.utils.event.MasterEvent(salt_config['sock_dir'])
        subscription.subscribe("ceph/services")

        while not self._complete.is_set():
            ev = subscription.get_event(tag="ceph/services")

            if ev is not None:
                log.info("ServerMonitor got ceph/services message from %s" % ev['id'])
                try:
                    # NB assumption that FQDN==minion_id is true unless
                    # someone has modded their salt minion config.
                    self.on_service_heartbeat(ev['id'], ev['data'])
                except:
                    log.debug("Message detail: %s" % json.dumps(ev))
                    log.exception("Error handling ceph/services message from %s" % ev['id'])

        log.info("Completed %s" % self.__class__.__name__)

    def get_hostname_to_osds(self, osd_map):
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
        For when a new OSD map is received: caller is responsible
        for processing the CRUSH map into a map of hostnames to OSD ids.

        :param osd_map: The data from an OsdMap sync object
        """
        log.debug("ServerMonitor.on_osd_map: epoch %s" % osd_map['epoch'])

        hostname_to_osds = self.get_hostname_to_osds(osd_map)
        log.debug("ServerMonitor.on_osd_map: got service data for %s servers" % len(hostname_to_osds))

        osds_in_map = set()
        for hostname, osds in hostname_to_osds.items():
            try:
                server_state = self.hostname_to_server[hostname]
            except KeyError:
                # Fake FQDN to equal hostname
                server_state = ServerState(hostname, hostname, managed=False, last_contact=None)
                self.inject_server(server_state)
                self._persister.create_server(Server(
                    fqdn=server_state.fqdn,
                    hostname=server_state.hostname,
                    managed=server_state.managed))

            for osd in osds:
                service_id = ServiceId(osd_map['fsid'], 'osd', str(osd['osd']))
                osds_in_map.add(service_id)
                if not server_state.managed:
                    # Only pay attention to these services for unmanaged servers,
                    # for managed servers rely on ceph/services salt messages
                    self._register_service(server_state, service_id, running=bool(osd['up']))

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
        pillar_util = salt.utils.master.MasterPillarUtil(fqdn, 'glob',
                                                         use_cached_grains=True,
                                                         grains_fallback=False,
                                                         opts=salt_config)
        try:
            return pillar_util.get_minion_grains()[fqdn]
        except KeyError:
            raise GrainsNotFound(fqdn)

    @nosleep
    def on_service_heartbeat(self, fqdn, services_data):
        """
        Call back for when a ceph.service message is received from a salt minion
        """
        log.debug("ServerMonitor.on_service_heartbeat: %s" % fqdn)
        # For any service which was last reported on this server but
        # is now gone, mark it as not running
        try:
            server_state = self.servers[fqdn]
        except KeyError:
            # Look up the grains for this server, we need to know its hostname in order
            # to resolve this vs. the OSD map.
            hostname = self._get_grains(fqdn)['host']

            new_server = True
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
                else:
                    # We will go on to treat these as distinct servers even though
                    # they have the same hostname
                    log.warn("Hostname clash: FQDNs '%s' and '%s' both have hostname %s" % (
                        fqdn, server_state.fqdn, hostname
                    ))

            if new_server:
                server_state = ServerState(fqdn, hostname, managed=True,
                                           last_contact=now())
                self.inject_server(server_state)
                self._persister.create_server(Server(
                    fqdn=server_state.fqdn,
                    hostname=server_state.hostname,
                    managed=server_state.managed,
                    last_contact=server_state.last_contact
                ))
                log.info("Saw server %s for the first time" % server_state)

        server_state.last_contact = now()
        self._persister.update_server(server_state.fqdn, last_contact=server_state.last_contact)

        seen_id_tuples = set()
        for service_name, service in services_data.items():
            id_tuple = ServiceId(service['fsid'], service['type'], service['id'])
            seen_id_tuples.add(id_tuple)
            self._register_service(server_state, id_tuple, running=True)

        for unseen_id_tuple in set(server_state.services.keys()) ^ seen_id_tuples:
            service_state = self.services[unseen_id_tuple]
            if service_state.running:
                log.info("Service %s stopped on server %s" % (service_state, server_state))
                service_state.running = False

    def _register_service(self, server_state, service_id, running):
        try:
            service_state = self.services[service_id]
        except KeyError:
            log.info("Saw service %s for the first time" % (service_id,))
            service_state = ServiceState(*service_id)
            self.inject_service(service_state, server_state.fqdn)

            self._persister.create_service(Service(
                fsid=service_state.fsid,
                service_type=service_state.service_type,
                service_id=service_state.service_id
            ), associate_fqdn=server_state.fqdn)

        if running != service_state.running:
            if running:
                log.info("Service %s started" % service_state)
                service_state.running = True
            else:
                log.info("Service %s stopped" % service_state)
                service_state.running = False

            self._persister.update_service(service_state.id, running=service_state.running)

        if service_state.server_state != server_state:
            old_server_state = service_state.server_state
            log.info("Associated service %s with server %s (was %s)" % (service_id, server_state, old_server_state))
            service_state.set_server(server_state)
            if old_server_state is not None:
                del old_server_state.services[service_id]
            server_state.services[service_id] = service_state
            self._persister.update_service_location(service_state.id, service_state.server_state.fqdn)

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

        """
        try:
            return self.services[service_id].server_state
        except KeyError:
            return None

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
        if not fsid in self.fsid_services:
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
            'services': [{'id': tuple(s.id), 'running': s.running} for s in server_state.services.values()]
        }

    def _addr_to_iface(self, addr, ip_interfaces):
        """
        Resolve an IP address to a network interface.

        :param addr: An address string like "1.2.3.4"
        :param ip_interfaces: The 'ip_interfaces' salt grain
        """
        for iface_name, iface_addrs in ip_interfaces.items():
            if addr in iface_addrs:
                return iface_name

        return None

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
                mon_map = cluster.get_sync_object(MonMap)
                if mon_map is not None:
                    mon = [mon for mon in mon_map['mons'] if mon['name'] == service.service_id][0]
                    frontend_addr = mon['addr'].split(":")[0]

            if (frontend_addr is None or backend_addr is None) and service.service_type == 'osd':
                # Go find the OSD in the OSD map and tell me its frontend and backend addrs
                osd_map = cluster.get_sync_object(OsdMap)
                if osd_map is not None:
                    osd = [osd for osd in osd_map['osds'] if str(osd['osd']) == service.service_id][0]
                    frontend_addr = osd['public_addr'].split(":")[0]
                    backend_addr = osd['cluster_addr'].split(":")[0]

        frontend_iface = None
        backend_iface = None
        try:
            grains = self._get_grains(server_state.fqdn)
        except GrainsNotFound:
            pass
        else:
            if frontend_addr:
                frontend_iface = self._addr_to_iface(frontend_addr, grains['ip_interfaces'])
            if backend_addr:
                backend_iface = self._addr_to_iface(backend_addr, grains['ip_interfaces'])

        return {
            'fqdn': server_state.fqdn,
            'hostname': server_state.hostname,
            'managed': server_state.managed,
            'last_contact': server_state.last_contact.isoformat() if server_state.last_contact else None,
            'services': [{'id': tuple(s.id), 'running': s.running} for s in services],
            'frontend_addr': frontend_addr,
            'backend_addr': backend_addr,
            'frontend_iface': frontend_iface,
            'backend_iface': backend_iface
        }
