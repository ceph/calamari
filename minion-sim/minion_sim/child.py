import os
import sys
import xmlrpclib
import yaml
from minion_sim.log import log

# Because salt minion will be calling functions
# defined in this module
__context__ = {}

FLAG_HASHPSPOOL = 1


def main():
    """
    This is a specialized launcher for salt-minion.

    The difference is that it substitutes some modules with mocked versions
    that get their data from an XMLRPC test-driving interface instead of
    from the real system.

    Set RPC_URL environment variable to point to an XMLRPC CephCluster simulator.

    """
    # Dirty arg parsing, I assume I will always be invoked with -c <config>
    config_file = sys.argv[2]
    config = yaml.load(open(os.path.join(config_file, 'minion')))
    fqdn = config['grains']['fqdn']

    __salt__ = None

    rpc_url = os.environ['RPC_URL']

    cluster = xmlrpclib.ServerProxy(rpc_url, allow_none=True)

    # Monkey-patch in a mock version of the ceph module
    def heartbeat():
        global __salt__
        report_clusters = {}

        services = {}
        cluster_name = cluster.get_name()

        for service in cluster.get_services(fqdn):
            service_name = "%s-%s.%s" % (cluster_name, service['type'], service['id'])
            services[service_name] = {
                'id': str(service['id']),
                'type': service['type'],
                'cluster': cluster_name,
                'fsid': service['fsid']
            }
            if service['type'] == 'mon':
                fsid = service['fsid']

                report_clusters[fsid] = cluster.get_heartbeat(fsid)

        __salt__['event.fire_master'](services, "ceph/server")
        for fsid, cluster_data in report_clusters.items():
            __salt__['event.fire_master'](cluster_data, 'ceph/cluster/{0}'.format(fsid))

    def get_cluster_object(cluster_name, sync_type, since):
        return cluster.get_cluster_object(cluster_name, sync_type, since)

    def rados_commands(fsid, cluster_name, commands):
        services = cluster.get_services(fqdn)
        fsid = None
        for service in services:
            fsid = service['fsid']
        assert fsid is not None

        for command in commands:
            prefix, args = command
            try:
                if prefix == "osd pool create":
                    cluster.pool_create(args['pool'], args['pg_num'])
                elif prefix == "osd pool set":
                    if args['var'] == 'hashpspool':
                        # 'set hashpspool' is actually and update to 'flags'
                        cluster.pool_update(args['pool'], "flags", FLAG_HASHPSPOOL if args['val'] else 0)
                    else:
                        cluster.pool_update(args['pool'], args['var'], args['val'])
                elif prefix == "osd pool set-quota":
                    # NB set-quota takes a string which it expects to parse
                    # as numeric size
                    cluster.pool_update(args['pool'], "quota_%s" % args['field'], int(args['val']))
                elif prefix == "osd pool rename":
                    cluster.pool_update(args['srcpool'], 'pool_name', args['destpool'])
                elif prefix == "osd pool delete":
                    cluster.pool_delete(args['pool'])
                else:
                    raise NotImplementedError()
            except Exception as e:
                status = cluster.get_heartbeat(fsid)
                return {
                    'error': True,
                    'results': [],
                    'err_outbuf': e.__str__(),
                    'err_outs': e.__str__(),
                    'fsid': fsid,
                    'versions': status['versions']
                }

        status = cluster.get_heartbeat(fsid)
        return {
            'error': False,
            'results': [None for n in commands],
            'err_outbuf': '',
            'err_outs': '',
            'fsid': fsid,
            'versions': status['versions']
        }

    import salt.loader

    old_minion_mods = salt.loader.minion_mods

    def my_minion_mods(opts):
        global __salt__
        data = old_minion_mods(opts)
        data['ceph.heartbeat'] = heartbeat
        data['ceph.get_cluster_object'] = get_cluster_object
        data['ceph.rados_commands'] = rados_commands
        __salt__ = data
        return data

    salt.loader.minion_mods = my_minion_mods

    try:
        minion = salt.Minion()
        minion.start()
    except Exception as e:
        if not isinstance(e, SystemExit):
            log.exception("minion.start[%s] threw an exception" % fqdn)
        raise
