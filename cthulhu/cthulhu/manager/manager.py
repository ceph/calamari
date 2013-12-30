import hashlib
import json
import gevent.event
import signal
from dateutil.tz import tzutc

import gevent
import salt
import zmq

import sqlalchemy
from sqlalchemy import create_engine

from cthulhu.log import log
from cthulhu.config import DB_PATH
from cthulhu.manager.cluster_monitor import ClusterMonitor, SALT_RUN_PATH
from cthulhu.manager.rpc import RpcThread
from cthulhu.persistence.sync_objects import Persister, Session, SyncObject


from gevent.monkey import patch_all
patch_all()
import zmq.green
import salt.utils.event
salt.utils.event.zmq = zmq.green


class DiscoveryThread(gevent.greenlet.Greenlet):
    def __init__(self, manager):
        super(DiscoveryThread, self).__init__()

        self._manager = manager
        self._complete = gevent.event.Event()

    def stop(self):
        self._complete.set()

    def _run(self):
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
        self._complete = gevent.event.Event()

        self._rpc_thread = RpcThread(self)
        self._discovery_thread = DiscoveryThread(self)

        # FSID to ClusterMonitor
        self.monitors = {}

        self._notifier = NotificationThread()
        try:
            # Prepare persistence
            engine = create_engine(DB_PATH)
            Session.configure(bind=engine)

            self._persister = Persister()
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
        victim.done.wait()
        del self.monitors[fs_id]

        self._expunge(fs_id)

    def stop(self):
        log.info("%s stopping" % self.__class__.__name__)
        for monitor in self.monitors.values():
            monitor.stop()
        self._rpc_thread.stop()
        self._discovery_thread.stop()
        self._notifier.stop()

    def _expunge(self, fsid):
        session = Session()
        session.query(SyncObject).filter_by(fsid=fsid).delete()
        session.commit()

    def _recover(self):
        # I want the most recent version of every sync_object
        session = Session()
        fsids = [row[0] for row in session.query(SyncObject.fsid).distinct(SyncObject.fsid)]
        for fsid in fsids:

            cluster_monitor = ClusterMonitor(fsid, 'ceph', self._notifier, self._persister)
            self.monitors[fsid] = cluster_monitor

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

                cluster_monitor.inject_sync_object(sync_type, version, json.loads(latest_record.data))

        for monitor in self.monitors.values():
            log.info("Recovery: Cluster %s with update time %s" % (monitor.fsid, monitor.update_time))
            monitor.start()

    def start(self):
        log.info("%s starting" % self.__class__.__name__)

        # Before we start listening to the outside world, recover
        # our last known state from persistent storage
        self._recover()

        self._rpc_thread.bind()
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


class NotificationThread(gevent.greenlet.Greenlet):
    """
    Responsible for:
     - Listening for Websockets clients connecting, and subscribing them
       to the ceph: topics
     - Publishing messages to Websockets topics on behalf of other
       python code.
    """
    def __init__(self):
        super(NotificationThread, self).__init__()
        self._complete = gevent.event.Event()
        self._pub = None
        self._ready = gevent.event.Event()

    def stop(self):
        self._complete.set()

    def publish(self, topic, message):
        self._ready.wait()
        self._pub.send(b'publish', zmq.SNDMORE)
        self._pub.send(topic, zmq.SNDMORE)
        self._pub.send(json.dumps(message))

    def _run(self):
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

    complete = gevent.event.Event()

    def shutdown():
        log.info("Signal handler: stopping")
        complete.set()

    gevent.signal(signal.SIGTERM, shutdown)
    gevent.signal(signal.SIGINT, shutdown)

    while not complete.is_set():
        complete.wait(timeout=1)