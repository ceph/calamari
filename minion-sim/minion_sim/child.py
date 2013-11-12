import os
import sys
import xmlrpclib
import yaml
from minion_sim.sim import XMLRPC_PORT


# Because salt minion will be calling functions
# defined in this module
__context__ = {}


def main():
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