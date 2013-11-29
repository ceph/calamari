import json
import threading
import signal

import gevent
import salt
import sqlalchemy
import zmq

from cthulhu.log import log
from cthulhu.config import DB_PATH
from cthulhu.manager.cluster_monitor import ClusterMonitor, SALT_RUN_PATH
from cthulhu.manager.rpc import RpcThread
from cthulhu.persistence.sync_objects import Persister


def enable_gevent():
    # We are using gevent because:
    #
    # - ZeroRPC requires it
    # - It is nice and efficient anyway.

    from gevent.monkey import patch_all
    patch_all()
    import zmq.green
    import salt.utils.event
    salt.utils.event.zmq = zmq.green

enable_gevent()


class DiscoveryThread(threading.Thread):
    def __init__(self, manager):
        super(DiscoveryThread, self).__init__()

        self._manager = manager
        self._complete = threading.Event()

    def stop(self):
        self._complete.set()

    def run(self):
        log.info("%s running" % self.__class__.__name__)
        event = salt.utils.event.MasterEvent(SALT_RUN_PATH)
        event.subscribe("ceph/heartbeat/")

        while not self._complete.is_set():
            data = event.get_event()
            if data is not None:
                try:
                    if 'tag' in data and data['tag'].startswith("ceph/heartbeat/"):
                        cluster_data = data['data']
                        if not cluster_data['fsid'] in self._manager.monitors:
                            self._manager.on_discovery(data['id'], cluster_data)
                        else:
                            log.debug("%s: heartbeat from existing cluster %s" % (
                                self.__class__.__name__, cluster_data['fsid']))
                    else:
                        # This does not concern us, ignore it
                        #log.debug("DiscoveryThread ignoring: %s" % data)
                        pass
                except:
                    log.debug("Message content: %s" % data)
                    log.exception("Exception handling message")

        log.info("%s complete" % self.__class__.__name__)


class Manager(object):
    """
    Manage a collection of ClusterMonitors.

    Subscribe to ceph/heartbeat events, and create a ClusterMonitor
    for any FSID we haven't seen before.
    """

    def __init__(self):
        self._complete = threading.Event()

        self._rpc_thread = RpcThread(self)
        self._discovery_thread = DiscoveryThread(self)

        # FSID to ClusterMonitor
        self.monitors = {}

        self._notifier = NotificationThread()
        # TODO: catch and handle DB connection problems gracefully
        try:
            self._persister = Persister(DB_PATH)
        except sqlalchemy.exc.ArgumentError as e:
            log.error("Database error: %s" % e)
            raise

    def delete_cluster(self, fs_id):
        """
        Note that the cluster will pop right back again if its
        still sending heartbeats.
        """
        victim = self.monitors[fs_id]
        victim.stop()
        victim.join()
        del self.monitors[fs_id]

    def stop(self):
        log.info("%s stopping" % self.__class__.__name__)
        for monitor in self.monitors.values():
            monitor.stop()
        self._rpc_thread.stop()
        self._discovery_thread.stop()
        self._notifier.stop()

    def start(self):
        log.info("%s starting" % self.__class__.__name__)
        self._rpc_thread.start()
        self._discovery_thread.start()
        self._notifier.start()
        self._persister.start()

    def join(self):
        log.info("%s joining" % self.__class__.__name__)
        self._rpc_thread.join()
        self._discovery_thread.join()
        self._notifier.join()
        self._persister.join()
        for monitor in self.monitors.values():
            monitor.join()

    def on_discovery(self, minion_id, heartbeat_data):
        log.info("on_discovery: {0}/{1}".format(minion_id, heartbeat_data['fsid']))
        cluster_monitor = ClusterMonitor(heartbeat_data['fsid'], heartbeat_data['name'],
                                         self._notifier, self._persister)
        self.monitors[heartbeat_data['fsid']] = cluster_monitor

        #persistence.get_or_create(
        #    heartbeat_data['name'],
        #    heartbeat_data['fsid']
        #)

        # Run before passing on the heartbeat, because otherwise the
        # syncs resulting from the heartbeat might not be received
        # by the monitor.
        cluster_monitor.start()
        cluster_monitor.on_heartbeat(minion_id, heartbeat_data)


class NotificationThread(threading.Thread):
    """
    Responsible for:
     - Listening for Websockets clients connecting, and subscribing them
       to the ceph: topics
     - Publishing messages to Websockets topics on behalf of other
       python code.
    """
    def __init__(self):
        super(NotificationThread, self).__init__()
        self._complete = threading.Event()
        self._pub = None
        self._ready = threading.Event()

    def stop(self):
        self._complete.set()

    def publish(self, topic, message):
        self._ready.wait()
        self._pub.send(b'publish', zmq.SNDMORE)
        self._pub.send(topic, zmq.SNDMORE)
        self._pub.send(json.dumps(message))

    def run(self):
        ctx = zmq.Context(1)
        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://172.16.79.128:7002')
        sub.setsockopt(zmq.SUBSCRIBE, b"")
        self._pub = ctx.socket(zmq.PUB)
        self._pub.connect('tcp://172.16.79.128:7003')
        self._ready.set()
        while not self._complete.is_set():
            try:
                parts = sub.recv_multipart(flags=zmq.NOBLOCK)
            except zmq.ZMQError:
                self._complete.wait(timeout=1)
                continue

            if parts[1] == b'connect':
                self._pub.send(b'subscribe', zmq.SNDMORE)
                self._pub.send(parts[0], zmq.SNDMORE)
                self._pub.send(b'ceph:completion')

                self._pub.send(b'subscribe', zmq.SNDMORE)
                self._pub.send(parts[0], zmq.SNDMORE)
                self._pub.send(b'ceph:sync')


def main():
    m = Manager()
    m.start()

    complete = threading.Event()

    def shutdown():
        log.info("Signal handler: stopping")
        complete.set()

    gevent.signal(signal.SIGTERM, shutdown)
    gevent.signal(signal.SIGINT, shutdown)

    while not complete.is_set():
        complete.wait(timeout=1)
