
from glob import glob
import hashlib
import os
import re
import socket
import subprocess
import tempfile
import time
import struct
import msgpack
import json

# Note: do not import ceph modules at this scope, otherwise this module won't be able
# to cleanly talk to us about systems where ceph isn't installed yet.

# We apply a timeout to librados communications, because otherwise a stuck mon
# would block our emission of heartbeat events
RADOS_TIMEOUT = 20

# FIXME: We probably can't assume that <clustername>.client.admin.keyring is always
# present, although this is the case on a nicely ceph-deploy'd system
RADOS_NAME = 'client.admin'


def fire_event(data, tag):
    """
    Emit a salt event to the master
    """
    __salt__['event.fire_master'](data, tag)  # noqa


class MonitoringError(Exception):
    pass


class RadosError(MonitoringError):
    """
    Something went wrong talking to Ceph with librados
    """
    pass


class AdminSocketError(MonitoringError):
    """
    Something went wrong talking to Ceph with a /var/run/ceph socket.
    """
    pass


def rados_command(cluster_handle, prefix, args=None, decode=True):
    """
    Safer wrapper for ceph_argparse.json_command, which raises
    Error exception instead of relying on caller to check return
    codes.

    Error exception can result from:
    * Timeout
    * Actual legitimate errors
    * Malformed JSON output

    return: Decoded object from ceph, or None if empty string returned.
            If decode is False, return a string (the data returned by
            ceph command)
    """
    if args is None:
        args = {}

    argdict = args.copy()
    argdict['format'] = 'json'

    import rados
    from ceph_argparse import json_command

    ret, outbuf, outs = json_command(cluster_handle,
                                     prefix=prefix,
                                     argdict=argdict,
                                     timeout=RADOS_TIMEOUT)
    if ret != 0:
        raise rados.Error(outs)
    else:
        if decode:
            if outbuf:
                try:
                    return json.loads(outbuf)
                except (ValueError, TypeError):
                    raise RadosError("Invalid JSON output for command {0}".format(argdict))
            else:
                return None
        else:
            return outbuf


# This function borrowed from /usr/bin/ceph: we should
# get ceph's python code into site-packages so that we
# can borrow things like this.
def admin_socket(asok_path, cmd, fmt=''):
    """
    Send a daemon (--admin-daemon) command 'cmd'.  asok_path is the
    path to the admin socket; cmd is a list of strings
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
            raise AdminSocketError('exception: ' + str(e))
        return ret

    try:
        cmd_json = do_sockio(asok_path,
                             json.dumps({"prefix": "get_command_descriptions"}))
    except Exception as e:
        raise AdminSocketError('exception getting command descriptions: ' + str(e))

    if cmd == 'get_command_descriptions':
        return cmd_json

    sigdict = parse_json_funcsigs(cmd_json, 'cli')
    valid_dict = validate_command(sigdict, cmd)
    if not valid_dict:
        raise AdminSocketError('invalid command')

    if fmt:
        valid_dict['format'] = fmt

    try:
        ret = do_sockio(asok_path, json.dumps(valid_dict))
    except Exception as e:
        raise AdminSocketError('exception: ' + str(e))

    return ret


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


def transform_crushmap(data, operation):
    """
    Invokes crushtool to compile or de-compile data when operation == 'set' or 'get'
    respectively
    returns (0 on success, transformed crushmap, errors)
    """
    # write data to a tempfile because crushtool can't handle stdin :(
    with tempfile.NamedTemporaryFile(delete=True) as f:
        f.write(data)
        f.flush()

        if operation == 'set':
            args = ["crushtool", "-c", f.name, '-o', '/dev/stdout']
        elif operation == 'get':
            args = ["crushtool", "-d", f.name]
        else:
            return 1, '', 'Did not specify get or set'

        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        return p.returncode, stdout, stderr


def rados_commands(fsid, cluster_name, commands):
    """
    Passing in both fsid and cluster_name, because the caller
    should always know both, and it saves this function the trouble
    of looking up one from the other.
    """

    import rados
    from ceph_argparse import json_command

    # Open a RADOS session
    cluster_handle = rados.Rados(name=RADOS_NAME, clustername=cluster_name, conffile='')
    cluster_handle.connect()

    results = []

    # Each command is a 2-tuple of a prefix followed by an argument dictionary
    for i, (prefix, argdict) in enumerate(commands):
        argdict['format'] = 'json'
        if prefix == 'osd setcrushmap':
            ret, stdout, outs = transform_crushmap(argdict['data'], 'set')
            if ret != 0:
                raise RuntimeError(outs)
            ret, outbuf, outs = json_command(cluster_handle, prefix=prefix, argdict={}, timeout=RADOS_TIMEOUT, inbuf=stdout)
        else:
            ret, outbuf, outs = json_command(cluster_handle, prefix=prefix, argdict=argdict, timeout=RADOS_TIMEOUT)
        if ret != 0:
            return {
                'error': True,
                'results': results,
                'error_status': outs,
                'versions': cluster_status(cluster_handle, cluster_name)['versions'],
                'fsid': fsid
            }
        if outbuf:
            results.append(json.loads(outbuf))
        else:
            results.append(None)

    # For all RADOS commands, we include the cluster map versions
    # in the response, so that the caller knows which versions to
    # wait for in order to see the consequences of their actions.
    # TODO: not all commands will require version info on completion, consider making
    # this optional.
    # TODO: we should endeavor to return something clean even if we can't talk to RADOS
    # enough to get version info
    versions = cluster_status(cluster_handle, cluster_name)['versions']

    # Success
    return {
        'error': False,
        'results': results,
        'error_status': '',
        'versions': versions,
        'fsid': fsid
    }


def ceph_command(cluster_name, command_args):
    """
    Run a Ceph CLI operation directly.  This is a fallback to allow
    manual execution of arbitrary commands in case the user wants to
    do something that is absent or broken in Calamari proper.

    :param cluster_name: Ceph cluster name, or None to run without --cluster argument
    :param command_args: Command line, excluding the leading 'ceph' part.
    """

    if cluster_name:
        args = ["ceph", "--cluster", cluster_name] + command_args
    else:
        args = ["ceph"] + command_args

    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    status = p.returncode

    return {
        'out': stdout,
        'err': stderr,
        'status': status
    }


def _get_config(cluster_name):
    """
    Given that a mon is running on this server, query its admin socket to get
    the configuration dict.

    :return JSON-encoded config object
    """

    try:
        mon_socket = glob("/var/run/ceph/{cluster_name}-mon.*.asok".format(cluster_name=cluster_name))[0]
    except IndexError:
        raise AdminSocketError("Cannot find mon socket for %s" % cluster_name)
    config_response = admin_socket(mon_socket, ['config', 'show'], 'json')
    return config_response


def get_cluster_object(cluster_name, sync_type, since):
    # TODO: for the synced objects that support it, support
    # fetching older-than-present versions to allow the master
    # to backfill its history.

    import rados
    from ceph_argparse import json_command

    # Check you're asking me for something I know how to give you
    assert sync_type in SYNC_TYPES

    # Open a RADOS session
    cluster_handle = rados.Rados(name=RADOS_NAME, clustername=cluster_name, conffile='')
    cluster_handle.connect()

    ret, outbuf, outs = json_command(cluster_handle,
                                     prefix='status',
                                     argdict={'format': 'json'},
                                     timeout=RADOS_TIMEOUT)
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
        ret, raw, outs = json_command(cluster_handle, prefix=command, argdict=kwargs, timeout=RADOS_TIMEOUT)
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
            }, timeout=RADOS_TIMEOUT)
            assert ret == 0
            data['tree'] = json.loads(raw)
            # FIXME: crush dump does not support an epoch argument, so this is potentially
            # from a higher-versioned OSD map than the one we've just read
            ret, raw, outs = json_command(cluster_handle, prefix="osd crush dump", argdict=kwargs,
                                          timeout=RADOS_TIMEOUT)
            assert ret == 0
            data['crush'] = json.loads(raw)

            ret, raw, outs = json_command(cluster_handle, prefix="osd getcrushmap", argdict={'epoch': version},
                                          timeout=RADOS_TIMEOUT)
            assert ret == 0

            ret, stdout, outs = transform_crushmap(raw, 'get')
            assert ret == 0
            data['crush_map_text'] = stdout
            data['osd_metadata'] = []

            for osd_entry in data['osds']:
                osd_id = osd_entry['osd']
                command = "osd metadata"
		argdict = {'id': osd_id}
		argdict.update(kwargs)
                ret, raw, outs = json_command(cluster_handle, prefix=command, argdict=argdict,
                                              timeout=RADOS_TIMEOUT)
                assert ret == 0
                updated_osd_metadata = json.loads(raw)
                updated_osd_metadata['osd'] = osd_id
                data['osd_metadata'].append(updated_osd_metadata)

    return {
        'type': sync_type,
        'fsid': fsid,
        'version': version,
        'data': data
    }


def get_boot_time():
    """
    Retrieve the 'btime' line from /proc/stat

    :return integer, seconds since epoch at which system booted
    """
    data = open('/proc/stat').read()
    return int(re.search('^btime (\d+)$', data, re.MULTILINE).group(1))


def get_heartbeats():
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
        server_heartbeat = {
            'services': {},
            'boot_time': get_boot_time(),
            'ceph_version': None
        }
        return server_heartbeat, {}

    # Map of FSID to path string string
    mon_sockets = {}
    # FSID string to cluster name string
    fsid_names = {}
    # Service name to service dict
    services = {}

    # For each admin socket, try to interrogate the service
    for filename in glob("/var/run/ceph/*.asok"):
        try:
            service_data = service_status(filename)
        except (rados.Error, MonitoringError):
            # Failed to get info for this service, stale socket or unresponsive,
            # exclude it from report
            pass
        else:
            if not service_data:
                continue

            service_name = "%s-%s.%s" % (service_data['cluster'], service_data['type'], service_data['id'])

            services[service_name] = service_data
            fsid_names[service_data['fsid']] = service_data['cluster']

            if service_data['type'] == 'mon' and service_data['status']['rank'] in service_data['status']['quorum']:
                # A mon in quorum is elegible to emit a cluster heartbeat
                mon_sockets[service_data['fsid']] = filename

    # Installed Ceph version (as oppose to per-service running ceph version)
    ceph_version_str = __salt__['pkg.version']('ceph')  # noqa
    if ceph_version_str:
        ceph_version = ceph_version_str
    else:
        ceph_version = None

    # For each ceph cluster with an in-quorum mon on this node, interrogate the cluster
    cluster_heartbeat = {}
    for fsid, socket_path in mon_sockets.items():
        try:
            cluster_handle = rados.Rados(name=RADOS_NAME, clustername=fsid_names[fsid], conffile='')
            cluster_handle.connect()
            cluster_heartbeat[fsid] = cluster_status(cluster_handle, fsid_names[fsid])
        except (rados.Error, MonitoringError):
            # Something went wrong getting data for this cluster, exclude it from our report
            pass

    server_heartbeat = {
        'services': services,
        'boot_time': get_boot_time(),
        'ceph_version': ceph_version
    }

    return server_heartbeat, cluster_heartbeat


def service_status(socket_path):
    """
    Given an admin socket path, learn all we can about that service
    """
    try:
        cluster_name, service_type, service_id = \
            re.match("^(.+?)-(.+?)\.(.+)\.asok$", os.path.basename(socket_path)).groups()
    except AttributeError:
        return None

    status = None
    # Interrogate the service for its FSID
    if service_type != 'mon':
        try:
            fsid = json.loads(admin_socket(socket_path, ['status'], 'json'))['cluster_fsid']
        except AdminSocketError:
            # older osd/mds daemons don't support 'status'; try our best
            config = json.loads(admin_socket(socket_path, ['config', 'get', 'fsid'], 'json'))
            fsid = config['fsid']
    else:
        # For mons, we send some extra info here, because if they're out
        # of quorum we may not find out from the cluster heartbeats, so
        # need to use the service heartbeats to detect that.
        status = json.loads(admin_socket(socket_path, ['mon_status'], 'json'))
        fsid = status['monmap']['fsid']

    version_response = admin_socket(socket_path, ['version'], 'json')
    if version_response is not None:
        service_version = json.loads(version_response)['version']
    else:
        service_version = None

    return {
        'cluster': cluster_name,
        'type': service_type,
        'id': service_id,
        'fsid': fsid,
        'status': status,
        'version': service_version
    }


def cluster_status(cluster_handle, cluster_name):
    """
    Get a summary of the status of a ceph cluster, especially
    the versions of the cluster maps.
    """
    # Get map versions from 'status'
    mon_status = rados_command(cluster_handle, "mon_status")
    status = rados_command(cluster_handle, "status")

    fsid = status['fsid']
    mon_epoch = status['monmap']['epoch']
    osd_epoch = status['osdmap']['osdmap']['epoch']
    mds_epoch = status['mdsmap']['epoch']

    # FIXME: even on a healthy system, 'health detail' contains some statistics
    # that change on their own, such as 'last_updated' and the mon space usage.
    # FIXME: because we're including the part with time skew data, this changes
    # all the time, should just skip that part.
    # Get digest of health
    health_digest = md5(rados_command(cluster_handle, "health", args={'detail': ''}, decode=False))

    # Get digest of brief pg info
    pgs_brief = rados_command(cluster_handle, "pg dump", args={'dumpcontents': ['pgs_brief']})
    pg_summary_digest = md5(msgpack.packb(pg_summary(pgs_brief)))

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
    while True:
        time.sleep(1)


def selftest_exception():
    """
    For self-test only.  Throw an exception
    """
    raise RuntimeError("This is a self-test exception")


def _heartbeat():
    """
    Send an event to the master with the terse status
    """
    service_heartbeat, cluster_heartbeat = get_heartbeats()

    fire_event(service_heartbeat, 'ceph/server')
    for fsid, cluster_data in cluster_heartbeat.items():
        fire_event(cluster_data, 'ceph/cluster/{0}'.format(fsid))

    # Return the emitted data because it's useful if debugging with salt-call
    return service_heartbeat, cluster_heartbeat


def heartbeat():
    try:
        _heartbeat()
    except:
        # Swallow exceptions to work around saltstack issue #11919 in
        # salt 2014.1.1.  If we emitted exceptions then it could cause
        # our scheduled task to stop execution.  Remove this behaviour
        # once the issue is fixed upstream and we are using a more
        # recent salt in calamari.
        pass
