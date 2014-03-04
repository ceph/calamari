import os
import sys
import xmlrpclib
import json
import yaml
import zlib
from minion_sim.log import log
import time

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

    def status_check():
        return {"SMART Health Status": "OK"}

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
                'fsid': service['fsid'],
                'status': None
            }
            if service['type'] == 'mon':
                fsid = service['fsid']
                report_clusters[fsid] = cluster.get_heartbeat(fsid)
                services[service_name]['status'] = cluster.get_cluster_object(fsid, 'mon_status', None)['data']

        __salt__['event.fire_master'](services, "ceph/server")
        for fsid, cluster_data in report_clusters.items():
            __salt__['event.fire_master'](cluster_data, 'ceph/cluster/{0}'.format(fsid))

    def get_cluster_object(cluster_name, sync_type, since):
        result = cluster.get_cluster_object(cluster_name, sync_type, since)

        if sync_type == 'pg_brief':
            result['data'] = zlib.compress(json.dumps(result['data']))

        return result

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
                elif prefix == "osd in":
                    for osd_id in args['ids']:
                        cluster.set_osd_state(int(osd_id), None, 1)
                elif prefix == "osd out":
                    for osd_id in args['ids']:
                        cluster.set_osd_state(int(osd_id), None, 0)
                elif prefix == "osd down":
                    for osd_id in args['ids']:
                        cluster.set_osd_state(int(osd_id), 0, None)
                elif prefix == "osd reweight":
                    cluster.set_osd_weight(args['id'], args['weight'])
                elif prefix == "osd scrub":
                    pass
                elif prefix == "osd deep-scrub":
                    pass
                elif prefix == "osd repair":
                    pass
                elif prefix == "osd set":
                    cluster.set_osd_flags(args['key'])
                else:
                    raise NotImplementedError()
            except Exception as e:
                log.exception("Exception running %s" % command)
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

    def list_logs(subpath):
        return ["ceph/ceph.log"]

    def tail(subpath, n_lines):
        return """2014-01-19 18:30:29.176592 mon.0 192.168.18.1:6789/0 463 : [INF] pgmap v163848: 1644 pgs: 1644 active+clean; 1040 GB data, 1993 GB used, 2954 GB / 4948 GB avail
2014-01-19 18:30:34.581473 osd.2 192.168.18.3:6801/8734 192 : [INF] 1.fb scrub ok
2014-01-19 18:30:39.184182 mon.0 192.168.18.1:6789/0 464 : [INF] pgmap v163849: 1644 pgs: 1644 active+clean; 1040 GB data, 1993 GB used, 2954 GB / 4948 GB avail
2014-01-19 18:30:59.357278 mon.0 192.168.18.1:6789/0 465 : [INF] pgmap v163850: 1644 pgs: 1643 active+clean, 1 active+clean+scrubbing+deep; 1040 GB data, 1993 GB used, 2954 GB / 4948 GB avail
2014-01-19 18:31:01.897580 mon.0 192.168.18.1:6789/0 466 : [INF] pgmap v163851: 1644 pgs: 1643 active+clean, 1 active+clean+scrubbing+deep; 1040 GB data, 1993 GB used, 2954 GB / 4948 GB avail
2014-01-19 18:31:11.663174 mon.0 192.168.18.1:6789/0 467 : [INF] pgmap v163852: 1644 pgs: 1643 active+clean, 1 active+clean+scrubbing+deep; 1040 GB data, 1993 GB used, 2954 GB / 4948 GB avail
2014-01-19 18:31:32.179999 osd.1 192.168.18.2:6801/6964 1929 : [INF] 0.64 deep-scrub ok
2014-01-19 18:31:34.917031 mon.0 192.168.18.1:6789/0 468 : [INF] pgmap v163853: 1644 pgs: 1644 active+clean; 1040 GB data, 1993 GB used, 2954 GB / 4948 GB avail
2014-01-19 18:32:01.002447 osd.1 192.168.18.2:6801/6964 1930 : [INF] 1.1ef deep-scrub ok
2014-01-19 18:32:05.062757 mon.0 192.168.18.1:6789/0 469 : [INF] pgmap v163854: 1644 pgs: 1643 active+clean, 1 active+clean+scrubbing+deep; 1040 GB data, 1993 GB used, 2954 GB / 4948 GB avail"""

    def selftest_wait(period):
        """
        For self-test only.  Wait for the specified period and then return None.
        """
        time.sleep(period)

    def selftest_block():
        """
        For self-test only.  Run forever
        """
        while True:
            time.sleep(1)

    def selftest_exception():
        """
        For self-test only.  Throw an exception
        """
        raise RuntimeError("This is a self-test exception")

    import salt.loader
    old_minion_mods = salt.loader.minion_mods

    def my_minion_mods(opts, context=None, whilelist=None):
        global __salt__
        data = old_minion_mods(opts)
        data['ceph.heartbeat'] = heartbeat
        data['wilyplugin.status_check'] = status_check
        data['ceph.get_cluster_object'] = get_cluster_object
        data['ceph.rados_commands'] = rados_commands
        data['log_tail.list_logs'] = list_logs
        data['log_tail.tail'] = tail
        data['ceph.selftest_wait'] = selftest_wait
        data['ceph.selftest_block'] = selftest_block
        data['ceph.selftest_exception'] = selftest_exception
        data['state.highstate'] = lambda: None
        data['saltutil.sync_modules'] = lambda: None
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
