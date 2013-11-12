from collections import defaultdict
import json
import uuid


class CephCluster(object):
    """
    An approximate simulation of a Ceph cluster.

    Use for driving test/demo environments.
    """

    @staticmethod
    def create(filename, fqdns, mon_count=3, osds_per_host=4, osd_overlap=False):
        """
        Generate initial state for a cluster
        """
        fsid = uuid.uuid4().__str__()
        name = 'ceph'

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

        objects = {}
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
        objects['osd_map'] = {
            'osds': [],
            'pools': []
        }

        for i in range(0, len(osd_hosts) * osds_per_host):
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
        objects['pg_brief'] = []
        for pool in objects['osd_map']['pools']:
            for pg_num in range(pool['pg_num']):
                pg_id = "%s.%s" % (pool['pool'], pg_num)
                # TODO: pseudorandom setting of 'up' and 'acting'
                objects['pg_brief'].append({
                    'pgid': pg_id,
                    'state': 'active+clean',
                    'up': [0, 1],
                    'acting': [0, 1]
                })

        json.dump({
                      'service_locations': service_locations,
                      'host_services': host_services,
                      'fsid': fsid,
                      'name': name,
                      'objects': objects
                  }, open(filename, 'w'))

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

    def __init__(self, filename):
        data = json.load(open(filename))
        self._service_locations = data['service_locations']
        self._host_services = defaultdict(list, data['host_services'])
        self._fsid = data['fsid']
        self._name = data['name']
        self._objects = data['objects']

        print "Loaded %s: %s" % (filename, self._host_services)