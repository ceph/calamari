
"""
While the cluster monitor pays attention to events about Ceph clusters (which
span non-disjoint sets of servers), the server monitor just pays attention to
individual hosts with no regard to the relations between them.
"""
from collections import defaultdict, namedtuple
import json

from gevent import greenlet
from gevent import event
import salt.utils.event
import salt.utils.master

from cthulhu.log import log
from cthulhu.manager import salt_config, config

# The type name for hosts and osds in the CRUSH map (if users have their
# own crush map they may have changed this), Ceph defaults are 'host' and 'osd'
from cthulhu.manager.types import OsdMap, MonMap

CRUSH_HOST_TYPE = config.get('cthulhu', 'crush_host_type')
CRUSH_OSD_TYPE = config.get('cthulhu', 'crush_osd_type')

# We get information about servers from:
# * The OSD map & the mon -- this will mention servers by hostname
# * The user, when they authorize or reject a minion key by FQDN
# * ceph.services messages, when they tell us about what Ceph
#   services are running on a particular FQDN


# Precendence:
# - If I have a ceph.services report then that is gospel
# - If I get a host->OSD mapping for a hostname that none
#   of my servers currently have, that's a new passive server.
# - If I get a host->OSD mapping for an OSD ID that is already
#   reported as running on a managed server, then... think about this in the morning: believe
#   the most recent information, or assume that for an OSD That has once been reported
#   on a managed server, we should only listen to managed servers about it forever?

# got to maintain a 2-way look up: server to services, service to server.


# tests: with only mons reporting in to cthulhu, inject OSD Map indicating
# existence of some other OSDs.


# OHAI
# CRUSH gives us the hostname for an OSD ID, the OSDmap itself also gives
# us frontend and backend network addresses for the OSD.  Therefore even
# for the unmanaged servers we should be able to list out their frontend
# and backend network addresses.
# Listing frontend/backend network addresses for servers only makes sense
# in the context of a particular cluster.  But not every server is in a cluster.
# It follows that we need two server resources: one global /server/<fqdn>/ and
# another /cluster/<fsid>/server/<fqdn>.  The former would have a list of services,
# and a list of network interfaces.  The latter would have a list of services
# in a particular cluster, and cluster-aware network interface/address information.


class GrainsNotFound(Exception):
    pass


class ServerState(object):
    """
    A Ceph server, may be something we have had a heartbeat from or
    may be something we learned about from Ceph.
    """
    def __init__(self, fqdn, hostname, managed):
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
                    log.debug("Got OSD %s" % osd["name"])
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

    def on_osd_map(self, osd_map):
        """
        For when a new OSD map is received: caller is responsible
        for processing the CRUSH map into a map of hostnames to OSD ids.

        :param osd_map: The data from an OsdMap sync object
        """
        log.debug("ServerMonitor.on_osd_map: epoch %s" % osd_map['epoch'])

        hostname_to_osds = self.get_hostname_to_osds(osd_map)
        log.debug("ServerMonitor.on_osd_map: got service data for %s servers" % len(hostname_to_osds))

        for hostname, osds in hostname_to_osds.items():
            try:
                server_state = self.hostname_to_server[hostname]
            except KeyError:
                # Fake FQDN to equal hostname
                server_state = ServerState(hostname, hostname, managed=False)
                self.hostname_to_server[hostname] = server_state
                self.servers[server_state.fqdn] = server_state
                # TODO persist creation

            # Managed servers should be telling us about their services
            # with ceph.services messages, disregard the CRUSH info for
            # these servers.
            if server_state.managed:
                continue

            for osd in osds:
                # TODO: remove ServiceState for any OSDs for this FSID which are not
                # mentioned in hostname_to_osds
                service_id = ServiceId(osd_map['fsid'], 'osd', str(osd['osd']))
                self._register_service(server_state, service_id, running=bool(osd['up']))

    def _get_grains(self, fqdn):
        pillar_util = salt.utils.master.MasterPillarUtil(fqdn, 'glob',
                                                         use_cached_grains=True,
                                                         grains_fallback=False,
                                                         opts=salt_config)
        try:
            return pillar_util.get_minion_grains()[fqdn]
        except KeyError:
            raise GrainsNotFound(fqdn)

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

            if hostname in self.hostname_to_server:
                # Take over a ServerState that was created from OSD map
                server_state = self.hostname_to_server[hostname]
                assert not server_state.managed
                server_state.managed = True
                # OSD map servers would have faked up FQDN as hostname, so clear that out
                del self.servers[server_state.fqdn]
                server_state.fqdn = fqdn
                self.servers[server_state.fqdn] = server_state
                # TODO persist update to ServerState.fqdn
            else:
                server_state = self.servers[fqdn] = ServerState(fqdn, hostname, managed=True)
                self.hostname_to_server[hostname] = server_state
            log.info("Saw server %s for the first time" % server_state)
            # TODO: emit persistence creation for the server

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

        # TODO: use cluster maps to delete service states when they are
        # no longer visible in maps (distinguish between service not running
        # and service doesn't exist any more)...

    def _register_service(self, server_state, service_id, running):
        try:
            service_state = self.services[service_id]
        except KeyError:
            log.info("Saw service %s for the first time" % (service_id,))
            service_state = self.services[service_id] = ServiceState(*service_id)
            service_state.set_server(server_state)
            server_state.services[service_id] = service_state
            self.fsid_services[service_id.fsid].append(service_state)
            # TODO: emit persistence creation for the service

        if running != service_state.running:
            if running:
                log.info("Service %s started" % service_state)
                service_state.running = True
            else:
                log.info("Service %s stopped" % service_state)
                service_state.running = False

            # TODO: emit persistence update for this service

        log.debug("Updating service %s %s %s" % (service_state, service_state.server_state, server_state))

        if service_state.server_state != server_state:
            old_server_state = service_state.server_state
            log.info("Associated service %s with server %s (was %s)" % (service_id, server_state, old_server_state))
            service_state.set_server(server_state)
            if old_server_state is not None:
                del old_server_state.services[service_id]
            server_state.services[service_id] = service_state
            # TODO: emit persistence update for the service

    def stop(self):
        self._complete.set()

    def get_all_cluster(self, fsid):
        """
        All the ServerStates which are involved in
        this cluster (i.e. hosting a service with this FSID)
        """
        return list(set([s.server_state for s in self.fsid_services[fsid] if s.server_state is not None]))

    def get_one_cluster(self, fsid, fqdn):
        """Give me all the ServerStates which are referred to by
        a service with this FSID"""
        return list(set([s.server_state for s in self.fsid_services[fsid] if s.server_state is not None]))

    def get_all(self):
        """Give me all the ServerStates"""
        return self.servers.values()

    def get_one(self, fqdn):
        """
        Give me a single ServerState, looked up by FQDN.
        """
        return self.servers[fqdn]

    def remove(self, fqdn):
        """
        Forget about this server.  Does not prevent it popping back into
        existence if we see reference to it in an incoming event.
        """
        server_state = self.servers[fqdn]
        for service in server_state.services.values():
            service.server_state = None
            del self.services[service.id]
            self.fsid_services[service.id.fsid].remove(service)

        del self.hostname_to_server[server_state.hostname]
        del self.servers[fqdn]
        # TODO: persist deletion

    def dump(self, server_state):
        """
        Convert a ServerState into a serializable format
        """
        return {
            'fqdn': server_state.fqdn,
            'hostname': server_state.hostname,
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
            'services': [{'id': tuple(s.id), 'running': s.running} for s in services],
            'frontend_addr': frontend_addr,
            'backend_addr': backend_addr,
            'frontend_iface': frontend_iface,
            'backend_iface': backend_iface
        }
