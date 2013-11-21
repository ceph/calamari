from collections import defaultdict
import hashlib
import json
import logging
import uuid
import random

KB = 1024
GIGS = 1024 * 1024 * 1024


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())
log.addHandler(logging.FileHandler("{0}.log".format(__name__)))


def md5(raw):
    hasher = hashlib.md5()
    hasher.update(raw)
    return hasher.hexdigest()


def flatten_dictionary(data, sep='.', prefix=None):
    """Produces iterator of pairs where the first value is
    the joined key names and the second value is the value
    associated with the lowest level key. For example::

      {'a': {'b': 10},
       'c': 20,
       }

    produces::

      [('a.b', 10), ('c', 20)]
    """
    for name, value in sorted(data.items()):
        fullname = sep.join(filter(None, [prefix, name]))
        if isinstance(value, dict):
            for result in flatten_dictionary(value, sep, fullname):
                yield result
        else:
            yield (fullname, value)


def _pool_template(name, pool_id, pg_num):
    """
    Format as in OSD map dump
    """
    return {
                'pool': pool_id,
                'pool_name': name,
                "flags": 0,
                "flags_names": "",
                "type": 1,
                "size": 2,
                "min_size": 1,
                "crush_ruleset": 2,
                "object_hash": 2,
                "pg_num": pg_num,
                "pg_placement_num": 64,
                "crash_replay_interval": 0,
                "last_change": "1",
                "auid": 0,
                "snap_mode": "selfmanaged",
                "snap_seq": 0,
                "snap_epoch": 0,
                "pool_snaps": {},
                "removed_snaps": "[]",
                "quota_max_bytes": 0,
                "quota_max_objects": 0,
                "tiers": [],
                "tier_of": -1,
                "read_tier": -1,
                "write_tier": -1,
                "cache_mode": "none",
                "properties": []
            }


def pseudorandom_subset(possible_values, n_select, selector):
    result = []
    for i in range(0, n_select):
        result.append(possible_values[hash(selector + i.__str__()) % len(possible_values)])
    return result


def get_hostname(fqdn):
    return fqdn.split(".")[0]


class CephCluster(object):
    """
    An approximate simulation of a Ceph cluster.

    Use for driving test/demo environments.
    """

    @staticmethod
    def create(filename, fqdns, mon_count=3, osds_per_host=4, osd_overlap=False, osd_size=2*GIGS):
        """
        Generate initial state for a cluster
        """
        fsid = uuid.uuid4().__str__()
        name = 'ceph_fake'

        mon_hosts = fqdns[0:mon_count]
        if osd_overlap:
            osd_hosts = fqdns[mon_count:]
        else:
            osd_hosts = fqdns

        service_locations = {
            "osd": {},
            "mon": {}
        }
        host_services = defaultdict(list)

        osd_id = 0
        for fqdn in osd_hosts:
            for i in range(0, osds_per_host):
                service_locations["osd"][osd_id] = fqdn
                host_services[fqdn].append({
                    'type': 'osd',
                    'id': osd_id,
                    'fsid': fsid
                })
                osd_id += 1

        for fqdn in mon_hosts:
            mon_id = get_hostname(fqdn)
            service_locations["mon"][mon_id] = fqdn
            host_services[fqdn].append({
                "type": "mon",
                "id": mon_id,
                'fsid': fsid
            })

        objects = dict()
        objects['health'] = {
            'detail': None,
            'health': {
                'health_services': [],
            },
            'overall_status': "HEALTH_OK",
            'summary': None,
            'timechecks': {}
        }

        # OSD map
        # =======
        osd_stats = {}
        objects['osd_map'] = {
            'epoch': 1,
            'osds': [],
            'pools': []
        }

        osd_count = len(osd_hosts) * osds_per_host

        for i in range(0, osd_count):
            # TODO populate public_addr and cluster_addr from imagined
            # interface addresses of servers
            osd_id = i
            objects['osd_map']['osds'].append({
                'osd': osd_id,
                'uuid': uuid.uuid4().__str__(),
                'up': 1,
                'in': 1,
                'last_clean_begin': 0,
                'last_clean_end': 0,
                'up_from': 0,
                'up_thru': 0,
                'down_at': 0,
                'lost_at': 0,
                'public_addr': "",
                'cluster_addr': "",
                'heartbeat_back_addr': "",
                'heartbeat_front_addr': "",
                "state": ["exists", "up"]
            })
            osd_stats[osd_id] = {
                'total_bytes': osd_size
            }

        for i, pool in enumerate(['data', 'metadata', 'rbd']):
            # TODO these should actually have a different crush ruleset etc each
            objects['osd_map']['pools'].append(_pool_template(pool, i, 64))

        objects['osd_tree'] = {"nodes": [
            {
                "id": -1,
                "name": "default",
                "type": "root",
                "type_id": 6,
                "children": []
            }
        ]}

        host_tree_id = -2
        for fqdn, services in host_services.items():
            # Entries for OSDs on this host
            for s in services:
                if s['type'] != 'osd':
                    continue

                objects['osd_tree']['nodes'].append({
                    "id": s['id'],
                    "name": "osd.%s" % s['id'],
                    "exists": 1,
                    "type": "osd",
                    "type_id": 0,
                    "status": "up",
                    "reweight": 1.0,
                    "crush_weight": 1.0,
                    "depth": 2
                })

            # Entry for the host itself
            objects['osd_tree']['nodes'].append({
                "id": host_tree_id,
                "name": get_hostname(fqdn),
                "type": "host",
                "type_id": 1,
                "children": [
                    s['id'] for s in services if s['type'] == 'osd'
                ]
            })
            host_tree_id -= 1

        # Mon status
        # ==========
        objects['mon_map'] = {
            'mons': [

            ],
            'quorum': []
        }
        for i, mon_fqdn in enumerate(mon_hosts):
            # TODO: populate addr
            objects['mon_map']['mons'].append({
                'rank': i,
                'name': get_hostname(mon_fqdn),
                'addr': ""
            })
            objects['mon_map']['quorum'].append(i)
        objects['mon_status'] = {
            "monmap": objects['mon_map'],
            "quorum": [m['rank'] for m in objects['mon_map']['mons']]
        }

        objects['mds_map'] = {
            "max_mds": 1,
            "in": [],
            "up": {}
        }

        # PG map
        # ======
        pg_stats = {}
        objects['pg_brief'] = []
        for pool in objects['osd_map']['pools']:
            n_replicas = pool['size']
            for pg_num in range(pool['pg_num']):
                pg_id = "%s.%s" % (pool['pool'], pg_num)
                osds = pseudorandom_subset(range(0, osd_count), n_replicas, pg_id)
                objects['pg_brief'].append({
                    'pgid': pg_id,
                    'state': 'active+clean',
                    'up': osds,
                    'acting': osds
                })

                pg_stats[pg_id] = {
                    'num_objects': 0,
                    'num_bytes': 0,
                    'num_bytes_wr': 0,
                    'num_bytes_rd': 0
                }

        json.dump({'service_locations': service_locations,
                   'host_services': host_services,
                   'fsid': fsid,
                   'name': name,
                   'objects': objects,
                   'osd_stats': osd_stats,
                   'pg_stats': pg_stats}, open(filename, 'w'))

    def get_services(self, fqdn):
        return self._host_services[fqdn]

    def get_heartbeat(self, fsid):
        return {
            'name': self._name,
            'fsid': self._fsid,
            'versions': {
                'health': md5(json.dumps(self._objects['health'])),
                'mds_map': 1,
                'mon_map': 1,
                'mon_status': 1,
                'osd_map': self._objects['osd_map']['epoch'],
                'osd_tree': 1,
                'pg_brief': md5(json.dumps(self._objects['pg_brief']))
            }
        }

    def get_cluster_object(self, cluster_name, sync_type, since):
        data = self._objects[sync_type]
        if sync_type == 'osd_map':
            version = data['epoch']
        elif sync_type == 'health' or sync_type == 'pg_brief':
            version = md5(json.dumps(data))
        else:
            version = 1

        return {
            'fsid': self._fsid,
            'version': version,
            'type': sync_type,
            'data': data
        }

    def _pg_id_to_osds(self, pg_id):
        # TODO: respect the pool's replication policy
        replicas = 2

        possible_osd_ids = [o['osd'] for o in self._objects['osd_map']['osds'] if o['in']]

        return pseudorandom_subset(possible_osd_ids, replicas, pg_id)

    def _object_id_to_pg(self, pool_id, object_id):
        pg_num = 0
        for p in self._objects['osd_map']['pools']:
            if p['pool'] == pool_id:
                pg_num = p['pg_num']
        if pg_num is 0:
            raise RuntimeError("Pool %s not found" % pool_id)

        return "{0}.{1}".format(pool_id, hash(object_id.__str__()) % pg_num)

    def rados_write(self, pool_id, n, size):
        # Pick a random base ID
        base_id = random.randint(0, 10000)

        for i in range(0, n):
            object_id = base_id + i
            pg_id = self._object_id_to_pg(pool_id, object_id)

            # Record the object's existence
            self._pg_stats[pg_id]['num_objects'] += 1
            self._pg_stats[pg_id]['num_bytes'] += size
            self._pg_stats[pg_id]['num_bytes_wr'] += size
            # NB assuming all other usage stats are calculated from
            # PG stats

    def set_osd_state(self, osd_id, up=None, osd_in=None):
        # Update OSD map
        dirty = False
        osd = [o for o in self._objects['osd_map']['osds'] if o['osd'] == osd_id][0]
        if up is not None and osd['up'] != up:
            log.debug("Mark OSD %s up=%s" % (osd_id, up))
            osd['up'] = up
            dirty = True
        if osd_in is not None and osd['in'] != osd_in:
            log.debug("Mark OSD %s in=%s" % (osd_id, osd_in))
            osd['in'] = osd_in
            dirty = True

        if not dirty:
            return

        log.debug("Advancing OSD map")
        self._objects['osd_map']['epoch'] += 1

        self._pg_monitor()
        self._update_health()

    def pool_create(self, pool_name, pg_num):
        if pool_name in [p['pool_name'] for p in self._objects['osd_map']['pools']]:
            return

        new_id = max([p['pool'] for p in self._objects['osd_map']['pools']]) + 1

        self._objects['osd_map']['pools'].append(
            _pool_template(pool_name, new_id, pg_num)
        )
        self._objects['osd_map']['epoch'] += 1

    def pool_update(self, pool_name, var, val):
        pool = [p for p in self._objects['osd_map']['pools'] if p['pool_name'] == pool_name][0]
        if pool[var] != val:
            pool[var] = val
            self._objects['osd_map']['epoch'] += 1

    def pool_delete(self, pool_name):
        if pool_name in [p['pool_name'] for p in self._objects['osd_map']['pools']]:
            self._objects['osd_map']['pools'] = [p for p in self._objects['osd_map']['pools'] if p['pool_name'] != pool_name]
            self._objects['osd_map']['epoch'] += 1

    def _pg_monitor(self, recovery_credits=0):
        """
        Crude facimile of the PG monitor.  For each PG, based on its
        current state and the state of its OSDs, update it: usually do
        nothing, maybe mark it stale, maybe remap it.
        """

        osds = dict([(osd['osd'], osd) for osd in self._objects['osd_map']['osds']])

        for pg in self._objects['pg_brief']:
            states = set(pg['state'].split('+'))
            primary_osd_id = pg['acting'][0]
            # Call a PG is stale if its primary OSD is down
            if osds[primary_osd_id]['in'] == 1 and osds[primary_osd_id]['up'] == 0:
                states.add('stale')
            else:
                states.discard('stale')

            # Call a PG active if any of its OSDs are in
            if any([osds[i]['in'] == 1 for i in pg['acting']]):
                states.add('active')
            else:
                states.discard('active')

            # Remap a PG if any of its OSDs are out
            if any([osds[i]['in'] == 0 for i in pg['acting']]):
                states.add('remapped')
                osd_ids = self._pg_id_to_osds(pg['pgid'])
                pg['up'] = osd_ids
                pg['acting'] = osd_ids

            # Call a PG clean if its not remapped and all its OSDs are in
            if all([osds[i]['in'] == 1 for i in pg['acting']]) and not 'remapped' in states:
                states.add('clean')
            else:
                states.discard('clean')

            if recovery_credits > 0 and 'remapped' in states:
                states.discard('remapped')
                recovery_credits -= 1
                log.debug("Recovered PG %s" % pg['pgid'])

            new_state = "+".join(sorted(list(states)))
            if pg['state'] != new_state:
                log.debug("New PG state %s: %s" % (pg['pgid'], new_state))
                pg['state'] = new_state

    def advance(self, t):
        RECOVERIES_PER_SECOND = 1
        self._pg_monitor(t * RECOVERIES_PER_SECOND)
        self._update_health()

    def _update_health(self):
        """
        Update the 'health' object based on the cluster maps
        """

        if any([pg['state'] != 'active+clean' for pg in self._objects['pg_brief']]):
            self._objects['health']['overall_status'] = "HEALTH_WARN"
        else:
            self._objects['health']['overall_status'] = "HEALTH_OK"

    def update_rates(self):
        pass
        # Reduce the PG stats across affected objects:
        # - The bytes per sec and IOPS per sec for the OSDs
        # - The bytes per sec and IOPs per sec for the pool
        # - The bytes per sec and packets per sec for the public
        #   and cluster network interfaces
        # - The bytes per sec and IOPs for the data and journal
        #   drives for the OSDs

    def get_stats(self, fqdn):
        stats = dict()
        hostname = fqdn.split('.')[0]

        # Server stats
        # =============
        cpu_count = 2
        cpu_stat_names = ['guest', 'guest_nice', 'idle', 'iowait', 'irq', 'nice', 'softirq', 'steal', 'system', 'user']
        cpu_stats = defaultdict(dict)

        for k in cpu_stat_names:
            cpu_stats['total'][k] = 0
        for cpu in range(cpu_count):
            # Junk stats to generate load on carbon/graphite
            for k in cpu_stat_names:
                v = random.random()
                cpu_stats["cpu{0}".format(cpu)][k] = random.random()
                cpu_stats['total'][k] += v

        stats.update(flatten_dictionary(cpu_stats, prefix="servers.{0}.cpu".format(hostname)))

        # Network stats
        # =============
        interfaces = ['em1', 'p1p1', 'p1p2']
        net_stats = defaultdict(dict)
        for interface in interfaces:
            for k in ['rx_byte', 'rx_compressed', 'rx_drop', 'rx_errors', 'rx_fifo', 'rx_frame', 'rx_multicast',
                      'rx_packets', 'tx_byte', 'tx_compressed', 'tx_drop', 'tx_errors', 'tx_fifo', 'tx_frame',
                      'tx_multicast', 'tx_packets']:
                net_stats[interface][k] = random.random()
        stats.update(flatten_dictionary(net_stats, prefix="servers.{0}.network".format(hostname)))

        # Service stats
        # =============

        # Cluster stats
        # =============
        leader_name = None
        if self._objects['mon_map']['quorum']:
            leader_id = self._objects['mon_map']['quorum'][0]
            leader = [m for m in self._objects['mon_map']['mons'] if m['rank'] == leader_id][0]
            leader_name = leader['name']

        if get_hostname(fqdn) == leader_name:
            pool_stats = defaultdict(lambda: dict(
                bytes_used=0,
                kb_used=0,
                objects=0
            ))

            for pg_id, pg_stats in self._pg_stats.items():
                pool_id = int(pg_id.split(".")[0])
                pool_stats[pool_id]['bytes_used'] += pg_stats['num_bytes']
                pool_stats[pool_id]['objects'] += pg_stats['num_objects']

            for s in pool_stats.values():
                s['kb_used'] = s['bytes_used'] / KB

            total_used = 0
            for pool_id, pstats in pool_stats.items():
                total_used += pstats['bytes_used']
                for k, v in pstats.items():
                    stats["ceph.{0}.pool.{1}.{2}".format(self._name, pool_id, k)] = v

            total_space = sum([o['total_bytes'] for o in self._osd_stats.values()])
            
            df_stats = {
                'total_space': total_space,
                'total_used': total_used,
                'total_avail': total_space - total_used
            }
            for k, v in df_stats.items():
                stats["ceph.{0}.df.{1}".format(self._name, k)] = v

        return stats.items()

    def save(self):
        dump = {
            'fsid': self._fsid,
            'name': self._name,
            'objects': self._objects,
            'osd_stats': self._osd_stats,
            'pg_stats': self._pg_stats,
            'service_locations': self._service_locations,
            'host_services': self._host_services
        }
        json.dump(dump, open(self._filename, 'w'))

    def get_service_fqdns(self, service_type):
        """
        Given a service type (mon or osd), return an iterable
        of FQDNs of servers where that type of service is running.
        """
        return self._service_locations[service_type].values()

    def __init__(self, filename):
        self._filename = filename
        data = json.load(open(self._filename))
        self._service_locations = data['service_locations']
        self._host_services = defaultdict(list, data['host_services'])
        self._fsid = data['fsid']
        self._name = data['name']

        # The public objects (health, OSD map, brief PG info, etc)
        # This is the subset the RADOS interface that Calamari needs
        self._objects = data['objects']

        # The hidden state (in real ceph this would be accessible but
        # we hide it so that we can use simplified versions of things
        # like the PG map)
        self._osd_stats = data['osd_stats']
        self._pg_stats = data['pg_stats']
