import gc
import greenlet
import logging
import signal
import sys
import traceback

import gevent.event
import gevent.greenlet

from ceph_bridge import ceph
from ceph_bridge import config
from ceph_bridge import log
from ceph_bridge.manager.cluster_monitor import ClusterMonitor
from ceph_bridge.manager.eventer import Eventer
from ceph_bridge.manager.rpc import EtcdThread
from ceph_bridge.manager.server_monitor import ServerMonitor
from ceph_bridge.persistence.persister import Persister

LOG = log.LOG

try:
    import msgpack
except ImportError:
    msgpack = None


class TopLevelEvents(gevent.greenlet.Greenlet):

    def __init__(self, manager):
        super(TopLevelEvents, self).__init__()

        self._manager = manager
        self._complete = gevent.event.Event()

    def stop(self):
        self._complete.set()

    def _run(self):
        log.info("%s running" % self.__class__.__name__)

        while not self._complete.is_set():
            data = ceph.heartbeat(heartbeat_type="cluster", discover=True)
            if data is not None:
                for tag, cluster_data in data.iteritems():
                    try:
                        if tag.startswith("ceph/cluster/"):
                            if not cluster_data[
                                    'fsid'
                            ] in self._manager.clusters:
                                self._manager.on_discovery(cluster_data)
                            else:
                                log.debug(
                                    "%s: heartbeat from existing"
                                    " cluster %s" % (
                                        self.__class__.__name__,
                                        cluster_data['fsid']
                                    )
                                )
                        else:
                            # This does not concern us, ignore it
                            log.debug("TopLevelEvents: ignoring %s" % tag)
                            pass
                    except Exception:
                        log.exception(
                            "Exception handling message tag=%s" % tag)
            gevent.sleep(3)

        log.info("%s complete" % self.__class__.__name__)


class Manager(object):
    """Manage a collection of ClusterMonitors.

    Subscribe to ceph/cluster events, and create a ClusterMonitor

    for any FSID we haven't seen before.

    """

    def __init__(self):
        self._complete = gevent.event.Event()

        self._user_request_thread = EtcdThread(self)
        self._discovery_thread = TopLevelEvents(self)
        self.persister = Persister()

        # FSID to ClusterMonitor
        self.clusters = {}

        # Generate events on state changes
        self.eventer = Eventer(self)

        # Handle all ceph/server messages after cluster is discovered to
        # maintain etcd schema
        self.servers = ServerMonitor(self.persister, self.eventer)

    def delete_cluster(self, fs_id):
        """Note that the cluster will pop right back again if it's

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
        self._user_request_thread.stop()
        self._discovery_thread.stop()
        self.eventer.stop()

    def _expunge(self, fsid):
        pass

    def _recover(self):
        log.debug("Recovered server")
        pass

    def start(self):
        log.info("%s starting" % self.__class__.__name__)
        self._user_request_thread.start()
        self._discovery_thread.start()
        self.persister.start()
        self.eventer.start()

        self.servers.start()

    def join(self):
        log.info("%s joining" % self.__class__.__name__)
        self._user_request_thread.join()
        self._discovery_thread.join()
        self.persister.join()
        self.eventer.join()
        self.servers.join()
        for monitor in self.clusters.values():
            monitor.join()

    def on_discovery(self, heartbeat_data):
        log.info("on_discovery: {0}".format(heartbeat_data['fsid']))
        cluster_monitor = ClusterMonitor(
            heartbeat_data['fsid'],
            heartbeat_data['name'],
            self.persister, self.servers,
            self.eventer
        )
        self.clusters[heartbeat_data['fsid']] = cluster_monitor

        # Run before passing on the heartbeat, because otherwise the
        # syncs resulting from the heartbeat might not be received
        # by the monitor.
        cluster_monitor.start()
        # Wait for ClusterMonitor to start accepting events before asking it
        # to do anything
        cluster_monitor.ready()
        cluster_monitor.on_heartbeat(heartbeat_data['id'], heartbeat_data)


def dump_stacks():
    """This is for use in debugging, especially using manhole

    """
    for ob in gc.get_objects():
        if not isinstance(ob, greenlet.greenlet):
            continue
        if not ob:
            continue
        log.error(''.join(traceback.format_stack(ob.gr_frame)))


def main():
    argv = sys.argv
    argv = [] if argv is None else argv
    log.setup_logging()
    config.parse_args(argv)
    logging.setup(config.CONF, "ceph_bridge")
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
