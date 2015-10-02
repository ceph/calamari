import argparse
import hashlib
import logging
import os
import gc
import time
import signal
import traceback
import resource
import sys

import gevent.event
import gevent.socket as socket
import greenlet
from dateutil.tz import tzutc
import gevent.greenlet


try:
    import msgpack
except ImportError:
    msgpack = None


from calamari_common.remote import get_remote
from cthulhu.log import log
import cthulhu.log
from cthulhu.util import Ticker
from cthulhu.manager.cluster_monitor import ClusterMonitor
from cthulhu.manager.eventer import Eventer
from cthulhu.manager.request_collection import RequestCollection
from cthulhu.manager import request_collection
from cthulhu.manager.rpc import RpcThread
from cthulhu.manager import config
from cthulhu.manager.server_monitor import ServerMonitor, ServerState, ServiceState


# sqlalchemy is optional: without it, all database writes will
# be silently dropped.
try:
    import sqlalchemy
except ImportError:
    sqlalchemy = None
else:
    import sqlalchemy.exc
    from sqlalchemy import create_engine

    from cthulhu.persistence.sync_objects import SyncObject
    from cthulhu.persistence.persister import Persister, Session
    from cthulhu.persistence.servers import Server, Service


# Manhole module optional for debugging.
try:
    import manhole
except ImportError:
    manhole = None


remote = get_remote()


class ProcessMonitorThread(gevent.greenlet.Greenlet):
    CARBON_HOST = "localhost"
    CARBON_PORT = 2003
    MONITOR_PERIOD = 30

    def __init__(self):
        super(ProcessMonitorThread, self).__init__()
        self._complete = gevent.event.Event()

        self._socket = None

    def stop(self):
        self._complete.set()

    def _close(self):
        if self._socket and not self._socket.closed:
            self._socket.close()
            self._socket = None

    def _emit_stats(self):
        try:
            if not self._socket:
                log.info("Opening carbon socket {0}:{1}".format(self.CARBON_HOST, self.CARBON_PORT))
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.connect((self.CARBON_HOST, self.CARBON_PORT))

            carbon_data = ""
            t = int(time.time())
            usage = resource.getrusage(resource.RUSAGE_SELF)
            for usage_field in ("utime", "stime", "maxrss", "ixrss", "idrss", "isrss", "minflt", "majflt",
                                "nswap", "inblock", "oublock", "msgsnd", "msgrcv", "nsignals", "nvcsw", "nivcsw"):
                val = getattr(usage, "ru_{0}".format(usage_field))
                log.debug("{0}: {1}".format(usage_field, val))
                carbon_data += "calamari.cthulhu.ru_{0} {1} {2}\n".format(usage_field, val, t)

            self._socket.sendall(carbon_data)
        except socket.gaierror, resource.error:
            log.exception("Failed to send debugging statistics")
            self._close()

    def _run(self):
        log.info("Running {0}".format(self.__class__.__name__))
        while not self._complete.is_set():
            # self._emit_stats()
            self._complete.wait(self.MONITOR_PERIOD)

        self._close()


class TopLevelEvents(gevent.greenlet.Greenlet):
    def __init__(self, manager):
        super(TopLevelEvents, self).__init__()

        self._manager = manager
        self._complete = gevent.event.Event()

    def stop(self):
        self._complete.set()

    def on_heartbeat(self, fqdn, data):
        if not data['fsid'] in self._manager.clusters:
            self._manager.on_discovery(fqdn, data)
        else:
            log.debug("%s: heartbeat from existing cluster %s" % (
                self.__class__.__name__, data['fsid']))

    def on_job(self, fqdn, jid, success, result, cmd, args):
        self._manager.requests.on_completion(fqdn, jid, success, result, cmd, args)

    def _run(self):
        log.info("%s running" % self.__class__.__name__)

        remote.listen(self._complete,
                      on_heartbeat=self.on_heartbeat,
                      on_job=self.on_job,
                      on_running_jobs=self._manager.requests.on_tick_response)

        log.info("%s complete" % self.__class__.__name__)


class Manager(object):
    """
    Manage a collection of ClusterMonitors.

    Subscribe to ceph/cluster events, and create a ClusterMonitor
    for any FSID we haven't seen before.
    """

    def __init__(self):
        self._complete = gevent.event.Event()

        self._rpc_thread = RpcThread(self)
        self._discovery_thread = TopLevelEvents(self)
        self._process_monitor = ProcessMonitorThread()

        if sqlalchemy is not None:
            try:
                # Prepare persistence
                engine = create_engine(config.get('cthulhu', 'db_path'))
                Session.configure(bind=engine)

                self.persister = Persister()
            except sqlalchemy.exc.ArgumentError as e:
                log.error("Database error: %s" % e)
                raise
        else:
            class NullPersister(object):
                def start(self):
                    pass

                def stop(self):
                    pass

                def join(self):
                    pass

                def __getattribute__(self, item):
                    if item.startswith('_'):
                        return object.__getattribute__(self, item)
                    else:
                        try:
                            return object.__getattribute__(self, item)
                        except AttributeError:
                            def blackhole(*args, **kwargs):
                                pass
                            return blackhole

            self.persister = NullPersister()

        # Remote operations
        self.requests = RequestCollection(self)
        self._request_ticker = Ticker(request_collection.TICK_PERIOD,
                                      lambda: self.requests.tick())

        # FSID to ClusterMonitor
        self.clusters = {}

        # Generate events on state changes
        self.eventer = Eventer(self)

        # Handle all ceph/server messages
        self.servers = ServerMonitor(self.persister, self.eventer, self.requests)

    def delete_cluster(self, fs_id):
        """
        Note that the cluster will pop right back again if it's
        still sending heartbeats.
        """
        victim = self.clusters[fs_id]
        victim.stop()
        victim.done.wait()
        del self.clusters[fs_id]

        self._expunge(fs_id)

    def stop(self):
        log.info("%s stopping" % self.__class__.__name__)
        for monitor in self.clusters.values():
            monitor.stop()
        self._rpc_thread.stop()
        self._discovery_thread.stop()
        self._process_monitor.stop()
        self.eventer.stop()
        self._request_ticker.stop()

    def _expunge(self, fsid):
        session = Session()
        session.query(SyncObject).filter_by(fsid=fsid).delete()
        session.commit()

    def _recover(self):
        if sqlalchemy is None:
            return

        session = Session()
        for server in session.query(Server).all():
            log.debug("Recovered server %s" % server.fqdn)
            assert server.boot_time is None or server.boot_time.tzinfo is not None  # expect timezone-aware DB backend
            self.servers.inject_server(ServerState(
                fqdn=server.fqdn,
                hostname=server.hostname,
                managed=server.managed,
                last_contact=server.last_contact,
                boot_time=server.boot_time,
                ceph_version=server.ceph_version
            ))

        for service in session.query(Service).all():
            if service.server:
                server = session.query(Server).get(service.server)
            else:
                server = None
            log.debug("Recovered service %s/%s/%s on %s" % (
                service.fsid, service.service_type, service.service_id, server.fqdn if server else None
            ))
            self.servers.inject_service(ServiceState(
                fsid=service.fsid,
                service_type=service.service_type,
                service_id=service.service_id
            ), server.fqdn if server else None)

        # I want the most recent version of every sync_object
        fsids = [(row[0], row[1]) for row in session.query(SyncObject.fsid, SyncObject.cluster_name).distinct(SyncObject.fsid)]
        for fsid, name in fsids:
            cluster_monitor = ClusterMonitor(fsid, name, self.persister, self.servers,
                                             self.eventer, self.requests)
            self.clusters[fsid] = cluster_monitor

            object_types = [row[0] for row in session.query(SyncObject.sync_type).filter_by(fsid=fsid).distinct()]
            for sync_type in object_types:
                latest_record = session.query(SyncObject).filter_by(
                    fsid=fsid, sync_type=sync_type).order_by(
                    SyncObject.version.desc(), SyncObject.when.desc())[0]

                # FIXME: bit of a hack because records persisted only store their 'version'
                # if it's a real counter version, underlying problem is that we have
                # underlying data (health, pg_brief) without usable version counters.
                def md5(raw):
                    hasher = hashlib.md5()
                    hasher.update(raw)
                    return hasher.hexdigest()

                if latest_record.version:
                    version = latest_record.version
                else:
                    version = md5(latest_record.data)

                when = latest_record.when
                when = when.replace(tzinfo=tzutc())
                if cluster_monitor.update_time is None or when > cluster_monitor.update_time:
                    cluster_monitor.update_time = when

                cluster_monitor.inject_sync_object(None, sync_type, version, msgpack.unpackb(latest_record.data))

        for monitor in self.clusters.values():
            log.info("Recovery: Cluster %s with update time %s" % (monitor.fsid, monitor.update_time))
            monitor.start()

    def start(self):
        log.info("%s starting" % self.__class__.__name__)

        # Before we start listening to the outside world, recover
        # our last known state from persistent storage
        try:
            self._recover()
        except:
            log.exception("Recovery failed")
            os._exit(-1)

        self._rpc_thread.bind()
        self._rpc_thread.start()
        self._discovery_thread.start()
        self._process_monitor.start()
        self.persister.start()
        self.eventer.start()
        self._request_ticker.start()

        self.servers.start()

    def join(self):
        log.info("%s joining" % self.__class__.__name__)
        self._rpc_thread.join()
        self._discovery_thread.join()
        self._process_monitor.join()
        self.persister.join()
        self.eventer.join()
        self._request_ticker.join()
        self.servers.join()
        for monitor in self.clusters.values():
            monitor.join()

    def on_discovery(self, minion_id, heartbeat_data):
        log.info("on_discovery: {0}/{1}".format(minion_id, heartbeat_data['fsid']))
        cluster_monitor = ClusterMonitor(heartbeat_data['fsid'], heartbeat_data['name'],
                                         self.persister, self.servers, self.eventer, self.requests)
        self.clusters[heartbeat_data['fsid']] = cluster_monitor

        # Run before passing on the heartbeat, because otherwise the
        # syncs resulting from the heartbeat might not be received
        # by the monitor.
        cluster_monitor.start()
        # Wait for ClusterMonitor to start accepting events before asking it
        # to do anything
        cluster_monitor.ready()
        cluster_monitor.on_heartbeat(minion_id, heartbeat_data)


def dump_stacks():
    """
    This is for use in debugging, especially using manhole
    """
    for ob in gc.get_objects():
        if not isinstance(ob, greenlet.greenlet):
            continue
        if not ob:
            continue
        log.error(''.join(traceback.format_stack(ob.gr_frame)))


def main():
    parser = argparse.ArgumentParser(description='Calamari management service')
    parser.add_argument('--debug', dest='debug', action='store_true',
                        default=False, help='print log to stdout')

    args = parser.parse_args()
    if args.debug:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(cthulhu.log.FORMAT))
        log.addHandler(handler)

    # Instruct salt to use the gevent version of ZMQ
    import zmq.green
    import salt.utils.event
    salt.utils.event.zmq = zmq.green

    if sqlalchemy is not None:
        # Set up gevent compatibility in psycopg2
        import psycogreen.gevent
        psycogreen.gevent.patch_psycopg()

    if manhole is not None:
        # Enable manhole for debugging.  Use oneshot mode
        # for gevent compatibility
        manhole.cry = lambda message: log.info("MANHOLE: %s" % message)
        manhole.install(oneshot_on=signal.SIGUSR1)

    m = Manager()
    m.start()

    complete = gevent.event.Event()

    def shutdown():
        log.info("Signal handler: stopping")
        complete.set()

    gevent.signal(signal.SIGTERM, shutdown)
    gevent.signal(signal.SIGINT, shutdown)

    while not complete.is_set():
        complete.wait(timeout=1)
