from SimpleXMLRPCServer import SimpleXMLRPCServer
import argparse
from collections import defaultdict
import getpass
import json
import os
import errno
import subprocess
import uuid
import xmlrpclib
from jinja2 import Template
import threading
import signal
import salt
import sys
import yaml

XMLRPC_PORT = 8761

MINION_CONFIG_TEMPLATE = """
master: localhost
id: {{ HOSTNAME }}
user: {{ USER }}
pidfile: {{ ROOT }}/var/run/salt-minion.pid
pki_dir: {{ ROOT }}/etc/pki
cachedir: {{ ROOT }}/var/cache
log_file: {{ ROOT }}/var/log/salt/minion
sock_dir: /tmp
grains:
    fqdn: {{ FQDN}}
    localhost: {{ HOSTNAME }}
    host: {{ HOSTNAME }}
    nodename: {{ HOSTNAME }}
"""

PREFIX = 'figment'
DOMAIN = 'imagination.com'
ROOT = os.getcwd()


class Minion(object):
    def __init__(self, index):
        super(Minion, self).__init__()

        self.ps = None
        self.hostname = "{0}{1:03d}".format(PREFIX, index)
        self.fqdn = "{0}.{1}".format(self.hostname, DOMAIN)

        path = os.path.join(ROOT, self.hostname)

        try:
            os.makedirs(path)
            os.makedirs(os.path.join(path, 'var/run'))
            os.makedirs(os.path.join(path, 'etc/salt'))
        except OSError, e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise

        config_str = Template(MINION_CONFIG_TEMPLATE).render(
            HOSTNAME=self.hostname,
            USER=getpass.getuser(),
            ROOT=path,
            FQDN=self.fqdn
        )

        config_filename = os.path.join(path, 'etc/salt/minion')
        open(config_filename, 'w').write(config_str)

        self.cmdline = ['-c', os.path.dirname(config_filename)]

    def start(self):
        print "Calling salt_minion.start"
        self.ps = subprocess.Popen(['minion-child'] + self.cmdline)

    def stop(self):
        self.ps.send_signal(signal.SIGTERM)
        out, err = self.ps.communicate()


#
#"""
#- eb15e37d-7f6d-44e8-ae7c-a5e2ba2a17f3:
#    ----------
#    fsid:
#        eb15e37d-7f6d-44e8-ae7c-a5e2ba2a17f3
#    name:
#        ceph
#    versions:
#        ----------
#        health:
#            63dc16c521047de5f119dc5830bb251d
#        mds_map:
#            1
#        mon_map:
#            1
#        mon_status:
#            16
#        osd_map:
#            714
#        osd_tree:
#            714
#        pg_brief:
#            ca5e1a30d24bad3d6f7637349a17a7fe
#"""


class CephCluster(object):
    @staticmethod
    def create(filename, fqdns, mon_count=3, osds_per_host=4, osd_overlap = False):
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
                    'up': [0,1],
                    'acting': [0,1]
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
#        health:
#            63dc16c521047de5f119dc5830bb251d
#        mds_map:
#            1
#        mon_map:
#            1
#        mon_status:
#            16
#        osd_map:
#            714
#        osd_tree:
#            714
#        pg_brief:
#            ca5e1a30d24bad3d6f7637349a17a7fe
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


# Because salt minion will be calling functions
# defined in this module
__context__ = {}


def child():
    """
    This is a specialized launcher for salt-minion.

    The difference is that it substitutes some modules with mocked versions
    that get their data from an XMLRPC test-driving interface instead of
    from the real system.
    """
    # Dirty arg parsing, I assume I will always be invoked with -c <config>
    config_file = sys.argv[2]
    config = yaml.load(open(os.path.join(config_file, 'minion')))
    fqdn = config['grains']['fqdn']

    __salt__ = None

    cluster = xmlrpclib.ServerProxy('http://localhost:%s' % XMLRPC_PORT, allow_none=True)

    # Monkey-patch in a mock version of the ceph module
    def heartbeat():
        global __salt__
        report_clusters = {}


        services = cluster.get_services(fqdn)
        for service in services:
            if service['type'] == 'mon':
                fsid = service['fsid']

                report_clusters[fsid] = cluster.get_heartbeat(fsid)

        for fsid, cluster_data in report_clusters.items():
            __salt__['event.fire_master'](cluster_data, 'ceph/heartbeat/{0}'.format(fsid))

    def get_cluster_object(cluster_name, sync_type, since):
        return cluster.get_cluster_object(cluster_name, sync_type, since)

    import salt.loader
    old_minion_mods = salt.loader.minion_mods

    def my_minion_mods(opts):
        global __salt__
        data = old_minion_mods(opts)
        data['ceph.heartbeat'] = heartbeat
        data['ceph.get_cluster_object'] = get_cluster_object
        __salt__ = data
        return data
    salt.loader.minion_mods = my_minion_mods

    minion = salt.Minion()
    minion.start()


def main():
    parser = argparse.ArgumentParser(description='Start simulated salt minions.')
    parser.add_argument('--count', dest='count', type=int, default=3, help='Number of simulated minions')
    args = parser.parse_args()

    minions = []
    for i in range(0, args.count):
        minions.append(Minion(i))

    if not os.path.exists('cluster.json'):
        CephCluster.create('cluster.json', [m.fqdn for m in minions])
    cluster = CephCluster('cluster.json')

    # Start an XMLRPC service for the minions' fake ceph plugins to
    # get their state
    server = SimpleXMLRPCServer(("localhost", XMLRPC_PORT), allow_none=True)
    server.register_instance(cluster)

    for minion in minions:
        minion.start()

    try:
        server.serve_forever()
        #complete = threading.Event()
        #while not complete.is_set():
        #    complete.wait(1)
    except KeyboardInterrupt:
        for minion in minions:
            minion.stop()
