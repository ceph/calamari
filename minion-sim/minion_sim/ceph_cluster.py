from collections import defaultdict
import json
import uuid
import random

KB = 1024
GIGS = 1024 * 1024 * 1024


def pseudorandom_subset(possible_values, n_select, selector):
    result = []
    for i in range(0, n_select):
        result.append(possible_values[hash(selector + i.__str__()) % len(possible_values)])
    return result


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
            service_locations["mon"][fqdn] = fqdn
            host_services[fqdn].append({
                "type": "mon",
                "id": fqdn,
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
            objects['osd_map']['pools'].append({
                'pool': i,
                'pool_name': pool,
                "flags": 0,
                "flags_names": "",
                "type": 1,
                "size": 2,
                "min_size": 1,
                "crush_ruleset": 2,
                "object_hash": 2,
                "pg_num": 64,
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
            })

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
                "name": fqdn,
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

            ]
        }
        for i, mon_fqdn in enumerate(mon_hosts):
            # TODO: populate addr
            objects['mon_map']['mons'].append({
                'rank': i,
                'name': mon_fqdn,
                'addr': ""
            })
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
                'health': 'xxx',
                'mds_map': 1,
                'mon_map': 1,
                'mon_status': 1,
                'osd_map': 1,
                'osd_tree': 1,
                'pg_brief': 'xxx'
            }
        }

    def get_cluster_object(self, cluster_name, sync_type, since):
        return {
            'fsid': self._fsid,
            'version': 1,
            'type': sync_type,
            'data': self._objects[sync_type]
        }

    def _pg_id_to_osds(self, pg_id):
        # TODO: respect the pool's replication policy
        replicas = 2

        # TODO: respect whether OSDs are in or out
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

    def add_objects(self, pool_id, n, size):
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

        # Network stats
        # =============

        # Service stats
        # =============

        # Cluster stats
        # =============
        # TODO track and respect who is mon leader,
        # temporarily just using mon 0
        if fqdn == self._objects['mon_map']['mons'][0]['name']:
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
            'pg_stats': self._pg_stats
        }
        json.dump(dump, open(self._filename, 'w'))

    def __init__(self, filename):
        self._filename = filename
        data = json.load(open(self._filename))
        self._service_locations = data['service_locations']
        self._host_services = defaultdict(list, data['host_services'])
        self._fsid = data['fsid']
        self._name = data['name']

        # The public objects (OSD map, brief PG info, etc)
        self._objects = data['objects']

        # The hidden state (in real ceph this would be accessible but
        # we hide it so that we can use simplified versions of things
        # like the PG map)
        self._osd_stats = data['osd_stats']
        self._pg_stats = data['pg_stats']
