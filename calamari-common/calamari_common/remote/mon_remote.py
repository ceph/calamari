from glob import glob
import hashlib
import subprocess
import re
import struct
import traceback
import uuid
import time
from calamari_common.remote.base import Unavailable, Remote
import gevent
from gevent.event import Event
from gevent.queue import Queue, Empty
from gevent import socket
import os
import msgpack
import json

import logging
log = logging.getLogger('calamari.remote.mon')

HEARTBEAT_PERIOD = 10

SRC_DIR = "/etc/ceph"
SOCKET_DIR = "/var/run/ceph"
LOG_DIR = None

if SRC_DIR and not SOCKET_DIR:
    SOCKET_DIR = os.path.join(SRC_DIR, "out")

if SRC_DIR and not LOG_DIR:
    LOG_DIR = os.path.join(SRC_DIR, "out")

if SRC_DIR:
    SOCKET_PREFIX = ""
else:
    SOCKET_PREFIX = "{cluster_name}-"

RADOS_TIMEOUT = 20
RADOS_NAME = 'client.admin'

SYNC_TYPES = ['mon_status',
              'mon_map',
              'osd_map',
              'mds_map',
              'pg_summary',
              'health',
              'config']

try:
    import rados
    from ceph_argparse import parse_json_funcsigs, validate_command, json_command
except ImportError:
    log.error("Error importing ceph modules, if you're using vstart set PYTHONPATH and LD_LIBRARY_PATH")
    raise


class AdminSocketError(rados.Error):
    pass


def md5(raw):
    hasher = hashlib.md5()
    hasher.update(raw)
    return hasher.hexdigest()


def get_ceph_version():
    # TODO: a salt-less query for install ceph package version
    return None


def rados_connect(cluster_name):
    if SRC_DIR:
        conf_file = os.path.join(SRC_DIR, "ceph.conf")
    else:
        conf_file = ''

    cluster_handle = rados.Rados(
        name=RADOS_NAME,
        clustername=cluster_name,
        conffile=conf_file)
    cluster_handle.connect(timeout=RADOS_TIMEOUT)

    return cluster_handle

# This function borrowed from /usr/bin/ceph: we should
# get ceph's python code into site-packages so that we
# can borrow things like this.
def admin_socket(asok_path, cmd, fmt=''):
    """
    Send a daemon (--admin-daemon) command 'cmd'.  asok_path is the
    path to the admin socket; cmd is a list of strings
    """

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


def _get_config(cluster_name):
    """
    Given that a mon is running on this server, query its admin socket to get
    the configuration dict.

    :return JSON-encoded config object
    """

    try:
        mon_socket = glob(os.path.join(SOCKET_DIR, (SOCKET_PREFIX + "mon.*.asok").format(cluster_name=cluster_name)))[0]
    except IndexError:
        raise AdminSocketError("Cannot find mon socket for %s" % cluster_name)
    config_response = admin_socket(mon_socket, ['config', 'show'], 'json')
    return config_response


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
                    raise rados.Error("Invalid JSON output for command {0}".format(argdict))
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


def rados_commands(fsid, cluster_name, commands):
    """
    Passing in both fsid and cluster_name, because the caller
    should always know both, and it saves this function the trouble
    of looking up one from the other.
    """
    # Open a RADOS session
    cluster_handle = rados_connect(cluster_name)
    results = []

    # Each command is a 2-tuple of a prefix followed by an argument dictionary
    for i, (prefix, argdict) in enumerate(commands):
        argdict['format'] = 'json'
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

    if SRC_DIR:
        ceph = [os.path.join(SRC_DIR, "ceph"), "-c", os.path.join(SRC_DIR, "ceph.conf")]
    else:
        ceph = ['ceph']

    if cluster_name:
        args = ceph + ["--cluster", cluster_name] + command_args
    else:
        args = ceph + command_args

    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    status = p.returncode

    return {
        'out': stdout,
        'err': stderr,
        'status': status
    }


def get_cluster_object(cluster_name, sync_type, since):
    # TODO: for the synced objects that support it, support
    # fetching older-than-present versions to allow the master
    # to backfill its history.

    # Check you're asking me for something I know how to give you
    assert sync_type in SYNC_TYPES

    # Open a RADOS session
    cluster_handle = rados_connect(cluster_name)

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

    if rados is None:
        log.debug("rados module not found")
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
    for filename in glob(os.path.join(SOCKET_DIR, "*.asok")):
        log.debug("Querying {0}".format(filename))
        try:
            service_data = service_status(filename)
        except rados.Error:
            # Failed to get info for this service, stale socket or unresponsive,
            # exclude it from report
            pass
        else:
            service_name = "%s-%s.%s" % (service_data['cluster'], service_data['type'], service_data['id'])

            services[service_name] = service_data
            fsid_names[service_data['fsid']] = service_data['cluster']

            if service_data['type'] == 'mon' and service_data['status']['rank'] in service_data['status']['quorum']:
                # A mon in quorum is elegible to emit a cluster heartbeat
                mon_sockets[service_data['fsid']] = filename

    # Installed Ceph version (as oppose to per-service running ceph version)
    ceph_version_str = get_ceph_version()
    if ceph_version_str:
        ceph_version = ceph_version_str
    else:
        ceph_version = None

    # For each ceph cluster with an in-quorum mon on this node, interrogate the cluster
    cluster_heartbeat = {}
    for fsid, socket_path in mon_sockets.items():
        try:
            cluster_handle = rados_connect(fsid_names[fsid])
            cluster_heartbeat[fsid] = cluster_status(cluster_handle, fsid_names[fsid])
        except rados.Error:
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
    match = re.match("^(.*)-(.*)\.(.*).asok$", os.path.basename(socket_path))
    if match:
        cluster_name, service_type, service_id = match.groups()
    else:
        # In vstart clusters naming is different
        assert SRC_DIR
        cluster_name = "ceph"
        service_type, service_id = re.match("^(.*)\.(.*).asok$", os.path.basename(socket_path)).groups()

    # Interrogate the service for its FSID
    config = json.loads(admin_socket(socket_path, ['config', 'get', 'fsid'], 'json'))
    fsid = config['fsid']

    status = None
    if service_type == 'mon':
        # For mons, we send some extra info here, because if they're out
        # of quorum we may not find out from the cluster heartbeats, so
        # need to use the service heartbeats to detect that.
        status = json.loads(admin_socket(socket_path, ['mon_status'], 'json'))

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


HEARTBEAT = 0
JOB = 1
SERVER_HEARTBEAT = 2
RUNNING_JOBS = 3


class MsgEvent(object):
    def __init__(self, kind, data):
        self.kind = kind
        self.data = data


def run_job(cmd, args):
    if cmd == "ceph.get_cluster_object":
        return get_cluster_object(
            args['cluster_name'],
            args['sync_type'],
            args['since'])
    else:
        raise NotImplemented(cmd)


def run_job_thread(generator, jid, cmd, args):
    success = True
    try:
        result = run_job(cmd, args)
    except:
        success = False
        result = traceback.format_exc()

    result = MsgEvent(JOB, {
        'id': socket.getfqdn(),
        'jid': jid,
        'success': success,
        'return': result,
        'fun': cmd,
        'fun_args': args
    })

    generator.complete(jid, result)

_generator = None


class MsgGenerator(gevent.Greenlet):
    def __init__(self):
        super(MsgGenerator, self).__init__()
        self._complete = Event()
        self._jobs = {}
        self._instances = []

        # FIXME: monkey patch the whole world
        # because the python side of librados
        # uses threading.Thread.  However, rados
        # itself will still do blocking on e.g.
        # connect(), so we probably need to wrap
        # librados in its own non-gevent python
        # process and RPC to it.
        from gevent import monkey
        monkey.patch_all()

    def register(self, instance):
        if instance not in self._instances:
            self._instances.append(instance)

    def _emit(self, msg_event):
        for instance in self._instances:
            instance.put(msg_event)

    def complete(self, jid, event):
        del self._jobs[jid]
        self._emit(event)

    def running_jobs(self):
        self._emit(MsgEvent(RUNNING_JOBS, [{'jid': jid} for jid in self._jobs.keys()]))

    def run_job(self, fqdn, cmd, args):
        if fqdn != socket.getfqdn():
            raise Unavailable()

        jid = uuid.uuid4().__str__()
        self._jobs[jid] = gevent.spawn(lambda: run_job_thread(jid, cmd, args))
        return jid

    def _run(self):
        try:
            while not self._complete.is_set():
                server_heartbeat, cluster_heartbeat = get_heartbeats()
                log.debug("server_heartbeat: %s" % server_heartbeat)
                log.debug("cluster_heartbeat: %s" % cluster_heartbeat)
                if server_heartbeat:
                    self._emit(MsgEvent(SERVER_HEARTBEAT, server_heartbeat))
                if cluster_heartbeat:
                    self._emit(MsgEvent(HEARTBEAT, cluster_heartbeat))

                self._complete.wait(HEARTBEAT_PERIOD)
        except:
            log.error(traceback.format_exc())
            raise


class MonRemote(Remote):
    """
A ``Remote`` implementation that runs directly on a Ceph mon or
``vstart.sh`` Ceph cluster.
    """

    def register(self):
        if self._generator is not None:
            return

        global _generator
        if _generator is None:
            _generator = MsgGenerator()
            _generator.start()

        self._generator = _generator

        self._generator.register(self)

    def __init__(self):
        self._generator = None

        self.fqdn = socket.getfqdn()
        self.hostname = socket.gethostname()

        self._events = Queue()


    def put(self, msg_event):
        self._events.put(msg_event)

    def run_job_sync(self, fqdn, cmd, args):
        """
        Run one python function from our remote module, and wait
        for a response or raise Unavailable
        """
        try:
            return run_job(cmd, args)
        except:
            raise Unavailable()

    def run_job(self, fqdn, cmd, args):
        """
        Start running a python function from our remote module,
        and return the job ID
        """
        return self._generator.run_job(fqdn, cmd, args)

    def get_local_metadata(self):
        """
        Return the metadata for this host that we are running
        on.
        """
        raise NotImplementedError()

    def get_remote_metadata(self, fqdns):
        """
        Return a dict of FQDN to grain dictionary for remote servers.

        Any servers for which metadata is not found will appear in the result
        with an empty dictionary
        """
        if fqdns == [self.fqdn]:
            return {
                self.fqdn: {
                    'host': self.hostname
                }
            }
        else:
            return dict([(f, {}) for f in fqdns])

    def get_heartbeat_period(self, fqdn):
        """
        Return the period in seconds between heartbeats
        """
        return HEARTBEAT_PERIOD

    def get_running(self, fqdns):
        """
        Send a request to discover which job IDs are running on
        the specified hosts.  Wait for the response with listen()
        """
        raise NotImplementedError()

    def cancel(self, fqdn, jid):
        """
        Send a request to cancel a job on a particular host.  There
        is no feedback about whether the cancellation really happened.
        """
        raise NotImplementedError()

    def auth_get(self, fqdn):
        """
        Get the authentication status of a host
        """
        raise NotImplementedError()

    def auth_list(self, status_filter):
        """
        Get the authentication status of all hosts whose statuses
        match `status_filter`.

        :param status_filter: An authentication state string, or None for no filter.
        """
        raise NotImplementedError()

    def auth_accept(self, fqdn):
        """
        Set authentication state for this host to AUTH_ACCEPTED
        """
        raise NotImplementedError()

    def auth_reject(self, fqdn):
        """
        Set authentication state for this host to AUTH_REJECTED
        """
        raise NotImplementedError()

    def auth_delete(self, fqdn):
        """
        Clear authentication state for this host
        """
        raise NotImplementedError()

    def listen(self, completion,
               on_heartbeat=None,
               on_job=None,
               on_server_heartbeat=None,
               on_running_jobs=None,
               fsid=None):
        """
        Subscribe to messages

        :param on_heartbeat: Callback for heartbeats
        :param on_job: Callback for job completions
        :param fsid: Optionally filter heartbeats to one FSID
        """

        self.register()

        while not completion.is_set():
            try:
                ev = self._events.get(timeout=1)
            except Empty:
                pass
            else:
                log.debug("listen: ev: %s" % ev.kind)
                if ev.kind == HEARTBEAT and on_heartbeat:
                    on_heartbeat(self.fqdn, ev.data)
                elif ev.kind == SERVER_HEARTBEAT and on_server_heartbeat:
                    on_server_heartbeat(self.fqdn, ev.data)
                elif ev.kind == JOB and on_job:
                    on_job(ev.data['id'],
                           ev.data['jid'],
                           ev.data['success'],
                           ev.data['return'],
                           ev.data['fun'],
                           ev.data['fun_args'])
                elif ev.kind == RUNNING_JOBS and on_running_jobs:
                    on_running_jobs(self.fqdn, ev.data)


        log.info("listen: complete")
