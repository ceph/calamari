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
import zlib

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


def memoize(function):
    memo = {}

    def wrapper(*args):
        if args in memo:
            return memo[args]
        else:
            rv = function(*args)
            memo[args] = rv
            return rv
    return wrapper


SYNC_TYPES = ['mon_status',
              'mon_map',
              'osd_map',
              'mds_map',
              'pg_map',
              'pg_brief',
              'health']


def md5(raw):
    hasher = hashlib.md5()
    hasher.update(raw)
    return hasher.hexdigest()


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
    cluster_handle = rados.Rados(name='client.admin', clustername=cluster_name, conffile='')
    cluster_handle.connect()

    ret, outbuf, outs = json_command(cluster_handle, prefix='status', argdict={'format': 'json'})
    status = json.loads(outbuf)
    #latest_version = {
    #    'mds': lambda s: s['mdsmap']['epoch'],
    #    'osd': lambda s: s['osdmap']['osdmap']['epoch'],
    #    'pg': lambda s: s['pgmap']['version'],
    #    'mon': lambda s: s['monmap']['epoch']
    #}[type](status)
    #
    fsid = status['fsid']

    command, kwargs, version_fn = {
        'mon_status': ('mon_status', {}, lambda d, r: d['election_epoch']),
        'mon_map': ('mon dump', {}, lambda d, r: d['epoch']),
        'osd_map': ('osd dump', {}, lambda d, r: d['epoch']),
        'mds_map': ('mds dump', {}, lambda d, r: d['epoch']),
        'pg_brief': ('pg dump', {'dumpcontents': ['pgs_brief']}, lambda d, r: md5(r)),
        'health': ('health', {'detail': ''}, lambda d, r: md5(r))
    }[sync_type]
    kwargs['format'] = 'json'
    ret, raw, outs = json_command(cluster_handle, prefix=command, argdict=kwargs)
    assert ret == 0

    if sync_type == 'pg_brief':
        data = zlib.compress(raw)
        version = version_fn(None, raw)
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

    :return None if ceph modules are unavailable, else a dict.

    """

    try:
        import rados
    except ImportError:
        return None

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

        services[service_name] = {
            'cluster': cluster_name,
            'type': service_type,
            'id': service_id,
            'fsid': fsid
        }
        fsid_names[fsid] = cluster_name

        if service_type == 'mon':
            mon_sockets[fsid] = filename

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
        'format': 'json', 'dumpcontents': ['pgs_brief'], 'fooffd': 'asdasd'})
    assert ret == 0
    pgs_brief_digest = md5(outbuf)

    return {
        'name': cluster_name,
        'fsid': fsid,
        'versions': {
            'mon_status': mon_status['election_epoch'],
            'mon_map': mon_epoch,
            'osd_map': osd_epoch,
            'mds_map': mds_epoch,
            'pg_brief': pgs_brief_digest,
            'health': health_digest
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
