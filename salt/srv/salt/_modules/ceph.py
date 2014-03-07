
from glob import glob
import hashlib
import os
import re
import socket
import time

# Default timeout for communicating with the Ceph REST API.
import struct

# Note: do not import ceph modules at this scope, otherwise this module won't be able
# to cleanly talk to us about systems where ceph isn't installed yet.
import msgpack

_REST_CLIENT_DEFAULT_TIMEOUT = 10.0

import json


def fire_event(data, tag):
    __salt__['event.fire_master'](data, tag)  # noqa


# >>> XXX unclean borrowed from open source ceph code XXX
def admin_socket(asok_path, cmd, format=''):
    """
    Send a daemon (--admin-daemon) command 'cmd'.  asok_path is the
    path to the admin socket; cmd is a list of strings; format may be
    set to one of the formatted forms to get output in that form
    (daemon commands don't support 'plain' output).
    """

    from ceph_argparse import parse_json_funcsigs, validate_command

    def do_sockio(path, cmd):
        """ helper: do all the actual low-level stream I/O """
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(path)
        try:
            sock.sendall(cmd + '\0')
            len_str = sock.recv(4)
            if len(len_str) < 4:
                raise RuntimeError("no data returned from admin socket")
            l, = struct.unpack(">I", len_str)
            ret = ''

            got = 0
            while got < l:
                bit = sock.recv(l - got)
                ret += bit
                got += len(bit)

        except Exception as e:
            raise RuntimeError('exception: ' + str(e))
        return ret

    try:
        cmd_json = do_sockio(asok_path,
                             json.dumps({"prefix": "get_command_descriptions"}))
    except Exception as e:
        #raise RuntimeError('exception getting command descriptions: ' + str(e))
        return None

    if cmd == 'get_command_descriptions':
        return cmd_json

    sigdict = parse_json_funcsigs(cmd_json, 'cli')
    valid_dict = validate_command(sigdict, cmd)
    if not valid_dict:
        raise RuntimeError('invalid command')

    if format:
        valid_dict['format'] = format

    try:
        ret = do_sockio(asok_path, json.dumps(valid_dict))
    except Exception as e:
        raise RuntimeError('exception: ' + str(e))

    return ret
# <<< XXX unclean XXX


SYNC_TYPES = ['mon_status',
              'mon_map',
              'osd_map',
              'mds_map',
              'pg_summary',
              'health',
              'config']


def md5(raw):
    hasher = hashlib.md5()
    hasher.update(raw)
    return hasher.hexdigest()


def pg_summary(pgs_brief):
    """
    Convert an O(pg count) data structure into an O(osd count) digest listing
    the number of PGs in each combination of states.
    """

    osds = {}
    pools = {}
    all_pgs = {}
    for pg in pgs_brief:
        for osd in pg['acting']:
            try:
                osd_stats = osds[osd]
            except KeyError:
                osd_stats = {}
                osds[osd] = osd_stats

            try:
                osd_stats[pg['state']] += 1
            except KeyError:
                osd_stats[pg['state']] = 1

        pool = int(pg['pgid'].split('.')[0])
        try:
            pool_stats = pools[pool]
        except KeyError:
            pool_stats = {}
            pools[pool] = pool_stats

        try:
            pool_stats[pg['state']] += 1
        except KeyError:
            pool_stats[pg['state']] = 1

        try:
            all_pgs[pg['state']] += 1
        except KeyError:
            all_pgs[pg['state']] = 1

    return {
        'by_osd': osds,
        'by_pool': pools,
        'all': all_pgs
    }


def rados_commands(fsid, cluster_name, commands):
    """
    Passing in both fsid and cluster_name, because the caller
    should always know both, and it saves this function the trouble
    of looking up one from the other.
    """
    import rados
    from ceph_argparse import json_command

    # Open a RADOS session
    cluster_handle = rados.Rados(name='client.admin', clustername=cluster_name, conffile='')
    cluster_handle.connect()

    results = []

    # TODO: clarify what err_outbuf and err_outs really are, maybe give them
    # more obvious names.

    # Each command is a 2-tuple of a prefix followed by an argument dictionary
    for i, (prefix, argdict) in enumerate(commands):
        argdict['format'] = 'json'
        ret, outbuf, outs = json_command(cluster_handle, prefix=prefix, argdict=argdict)
        if ret != 0:
            return {
                'error': True,
                'results': results,
                'err_outbuf': outbuf,
                'err_outs': outs,
                'versions': cluster_status(cluster_handle, cluster_name)['versions'],
                'fsid': fsid
            }
        if outbuf:
            results.append(json.loads(outbuf))
        else:
            results.append(None)

    # Return map versions after executing commands, so that the Calamari server
    # knows which versions to wait for in order to make the results of this
    # command readable for its own clients.
    # TODO: not all commands will require version info on completion, consider making
    # this optional.
    # TODO: we should endeavor to return something clean even if we can't talk to RADOS
    # enough to get version info
    # TODO: use the cluster_handle we already have here instead of letting terse_status
    # create a new one (true other places in this module, requires general cleanup)

    # For all RADOS commands, we include the cluster map versions
    # in the response, so that the caller knows which versions to
    # wait for in order to see the consequences of their actions.

    # Success
    return {
        'error': False,
        'results': results,
        'err_outbuf': '',
        'err_outs': '',
        'versions': cluster_status(cluster_handle, cluster_name)['versions'],
        'fsid': fsid
    }


def _get_config(cluster_name):
    """
    :return JSON-encoded config object
    """

    try:
        mon_socket = glob("/var/run/ceph/{cluster_name}-mon.*.asok".format(cluster_name=cluster_name))[0]
    except IndexError:
        raise RuntimeError("Cannot find mon socket for %s" % cluster_name)
    config_response = admin_socket(mon_socket, ['config', 'show'], 'json')
    if not config_response:
        raise RuntimeError("Cannot contact mon for %s to get config" % cluster_name)
    return config_response


def get_cluster_object(cluster_name, sync_type, since):
    # TODO: for the synced objects that support it, support
    # fetching older-than-present versions to allow the master
    # to backfill its history.

    # This should only ever be called in response to
    # having already talked to ceph, so assume modules
    # are present
    import rados
    from ceph_argparse import json_command

    # Check you're asking me for something I know how to give you
    assert sync_type in SYNC_TYPES

    # Open a RADOS session
    try:
        cluster_handle = rados.Rados(name='client.admin', clustername=cluster_name, conffile='')
    except:
        raise RuntimeError("cluster_name = %s" % cluster_name)
    cluster_handle.connect()

    ret, outbuf, outs = json_command(cluster_handle, prefix='status', argdict={'format': 'json'})
    status = json.loads(outbuf)
    fsid = status['fsid']

    if sync_type == 'config':
        # Special case for config, get this via admin socket instead of librados
        raw = _get_config(cluster_name)
        version = md5(raw)
        data = json.loads(raw)
    else:
        command, kwargs, version_fn = {
            'mon_status': ('mon_status', {}, lambda d, r: d['election_epoch']),
            'mon_map': ('mon dump', {}, lambda d, r: d['epoch']),
            'osd_map': ('osd dump', {}, lambda d, r: d['epoch']),
            'mds_map': ('mds dump', {}, lambda d, r: d['epoch']),
            'pg_summary': ('pg dump', {'dumpcontents': ['pgs_brief']}, lambda d, r: md5(msgpack.packb(d))),
            'health': ('health', {'detail': ''}, lambda d, r: md5(r))
        }[sync_type]
        kwargs['format'] = 'json'
        ret, raw, outs = json_command(cluster_handle, prefix=command, argdict=kwargs)
        assert ret == 0

        if sync_type == 'pg_summary':
            data = pg_summary(json.loads(raw))
            version = version_fn(data, raw)
        else:
            data = json.loads(raw)
            version = version_fn(data, raw)

        # Internally, the OSDMap includes the CRUSH map, and the 'osd tree' output
        # is generated from the OSD map.  We synthesize a 'full' OSD map dump to
        # send back to the calamari server.
        if sync_type == 'osd_map':
            ret, raw, outs = json_command(cluster_handle, prefix="osd tree", argdict={
                'format': 'json',
                'epoch': version
            })
            assert ret == 0
            data['tree'] = json.loads(raw)
            # FIXME: crush dump does not support an epoch argument, so this is potentially
            # from a higher-versioned OSD map than the one we've just read
            ret, raw, outs = json_command(cluster_handle, prefix="osd crush dump", argdict=kwargs)
            assert ret == 0
            data['crush'] = json.loads(raw)

    return {
        'type': sync_type,
        'fsid': fsid,
        'version': version,
        'data': data
    }


def terse_status():
    """
    The goal here is *not* to give a helpful summary of
    the cluster status, rather it is to give the minimum
    amount if information to let an informed master decide
    whether it needs to ask us for any additional information,
    such as updated copies of the cluster maps.

    Enumerate Ceph services running locally, for each report
    its FSID, type and ID.

    If a mon is running here, do some extra work:

    - Report the mapping of cluster name to FSID from /etc/ceph/<cluster name>.conf
    - For all clusters, report the latest versions of all cluster maps.

    :return A 2-tuple of dicts for services, clusters

    """

    try:
        import rados
    except ImportError:
        # Ceph isn't installed, report no services or clusters
        return {}, {}

    services = {}

    # Map of FSID to path string string
    mon_sockets = {}

    # FSID string to cluster name string
    fsid_names = {}

    for filename in glob("/var/run/ceph/*.asok"):
        cluster_name, service_type, service_id = re.match("^(.*)-(.*)\.(.*).asok$", os.path.basename(filename)).groups()
        service_name = "%s-%s.%s" % (cluster_name, service_type, service_id)

        # Interrogate the service for its FSID
        config_response = admin_socket(filename, ['config', 'get', 'fsid'], 'json')
        if config_response is None:
            # Dead socket, defunct service
            continue

        config = json.loads(config_response)
        fsid = config['fsid']

        status = None
        if service_type == 'mon':
            # For mons, we send some extra info here, because if they're out
            # of quorum we may not find out from the cluster heartbeats, so
            # need to use the service heartbeats to detect that.
            status = json.loads(admin_socket(filename, ['mon_status'], 'json'))

            if status['rank'] in status['quorum']:
                # A mon in quorum is elegible to emit a cluster heartbeat
                mon_sockets[fsid] = filename

        services[service_name] = {
            'cluster': cluster_name,
            'type': service_type,
            'id': service_id,
            'fsid': fsid,
            'status': status
        }
        fsid_names[fsid] = cluster_name

    clusters = {}
    for fsid, socket_path in mon_sockets.items():
        # First, are we quorate?
        admin_response = admin_socket(socket_path, ['mon_status'], 'json')
        if admin_response is None:
            # Dead socket, defunct service
            continue
        mon_status = json.loads(admin_response)

        if not mon_status['quorum']:
            continue

        # FIXME 1: We probably can't assume that <clustername>.client.admin.keyring is always
        # present, although this is the case on a nicely ceph-deploy'd system
        # FIXME 2: It shouldn't really be necessary to fire up a RADOS client to obtain this
        # information, instead we should be able to get it from the mon admin socket.
        cluster_handle = rados.Rados(name='client.admin', clustername=fsid_names[fsid], conffile='')
        cluster_handle.connect()

        clusters[fsid] = cluster_status(cluster_handle, fsid_names[fsid])

    return services, clusters


def cluster_status(cluster_handle, cluster_name):
    from ceph_argparse import json_command

    # FIXME: error handling leaves a little to be desired: handle case where the cluster becomes
    # unavailable partway through these queries
    # Get map versions from 'status'

    ret, outbuf, outs = json_command(cluster_handle, prefix='mon_status', argdict={'format': 'json'})
    assert ret == 0
    mon_status = json.loads(outbuf)

    ret, outbuf, outs = json_command(cluster_handle, prefix='status', argdict={'format': 'json'})
    assert ret == 0
    status = json.loads(outbuf)

    fsid = status['fsid']
    mon_epoch = status['monmap']['epoch']
    osd_epoch = status['osdmap']['osdmap']['epoch']
    mds_epoch = status['mdsmap']['epoch']

    # FIXME: even on a healthy system, 'health detail' contains some statistics
    # that change on their own, such as 'lasted_updated' and the mon space usage.
    # Get digest of health
    ret, outbuf, outs = json_command(cluster_handle, prefix='health', argdict={
        'format': 'json',
        'detail': 'detail'
    })
    assert ret == 0
    # FIXME: because we're including the part with time skew data, this changes
    # all the time, should just skip that part.
    health_digest = md5(outbuf)

    # Get digest of brief pg info
    ret, outbuf, outs = json_command(cluster_handle, prefix='pg dump', argdict={
        'format': 'json', 'dumpcontents': ['pgs_brief']})
    assert ret == 0
    pg_summary_digest = md5(msgpack.packb(pg_summary(json.loads(outbuf))))

    # Get digest of configuration
    config_digest = md5(_get_config(cluster_name))

    return {
        'name': cluster_name,
        'fsid': fsid,
        'versions': {
            'mon_status': mon_status['election_epoch'],
            'mon_map': mon_epoch,
            'osd_map': osd_epoch,
            'mds_map': mds_epoch,
            'pg_summary': pg_summary_digest,
            'health': health_digest,
            'config': config_digest
        }
    }


def selftest_wait(period):
    """
    For self-test only.  Wait for the specified period and then return None.
    """
    time.sleep(period)


def selftest_block():
    """
    For self-test only.  Run forever
    """
    while(True):
        time.sleep(1)


def selftest_exception():
    """
    For self-test only.  Throw an exception
    """
    raise RuntimeError("This is a self-test exception")


def heartbeat():
    """
    Send an event to the master with the terse status
    """
    services, clusters = terse_status()

    fire_event(services, 'ceph/server')
    for fsid, cluster_data in clusters.items():
        fire_event(cluster_data, 'ceph/cluster/{0}'.format(fsid))

    # Return the emitted data because it's useful if debugging with salt-call
    return services, clusters


if __name__ == '__main__':
    # Debug, just dump everything
    print json.dumps(terse_status(), indent=2)
    for typ in SYNC_TYPES:
        get_cluster_object('ceph', typ, 0)
