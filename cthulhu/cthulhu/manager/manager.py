import argparse
import hashlib
import json
import logging
import gevent.event
import signal
from dateutil.tz import tzutc

import gevent.greenlet
import salt.utils.event
import sys

import sqlalchemy.exc
from sqlalchemy import create_engine

from cthulhu.log import log
import cthulhu.log
from cthulhu.manager.cluster_monitor import ClusterMonitor
from cthulhu.manager.eventer import Eventer
from cthulhu.manager.rpc import RpcThread
from cthulhu.manager.notifier import NotificationThread
from cthulhu.manager import config, salt_config
from cthulhu.manager.server_monitor import ServerMonitor, ServerState, ServiceState
from cthulhu.persistence.servers import Server, Service

from cthulhu.persistence.sync_objects import SyncObject
from cthulhu.persistence.persister import Persister, Session


class DiscoveryThread(gevent.greenlet.Greenlet):
    def __init__(self, manager):
        super(DiscoveryThread, self).__init__()

        self._manager = manager
        self._complete = gevent.event.Event()

    def stop(self):
        self._complete.set()

    def _run(self):
        log.info("%s running" % self.__class__.__name__)
        event = salt.utils.event.MasterEvent(salt_config['sock_dir'])
        event.subscribe("ceph/cluster/")

        while not self._complete.is_set():
            data = event.get_event(tag="ceph/cluster/")
            if data is not None:
                try:
                    if 'tag' in data and data['tag'].startswith("ceph/cluster/"):
                        cluster_data = data['data']
                        if not cluster_data['fsid'] in self._manager.clusters:
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

    Subscribe to ceph/cluster events, and create a ClusterMonitor
    for any FSID we haven't seen before.
    """

    def __init__(self):
        self._complete = gevent.event.Event()

        self._rpc_thread = RpcThread(self)
        self._discovery_thread = DiscoveryThread(self)

        self.notifier = NotificationThread()
        try:
            # Prepare persistence
            engine = create_engine(config.get('cthulhu', 'db_path'))
            Session.configure(bind=engine)

            self.persister = Persister()
        except sqlalchemy.exc.ArgumentError as e:
            log.error("Database error: %s" % e)
            raise

        # FSID to ClusterMonitor
        self.clusters = {}

        # Generate events on state changes
        self.eventer = Eventer(self)

        # Handle all ceph/server messages
        self.servers = ServerMonitor(self.persister, self.eventer)

    def delete_cluster(self, fs_id):
        """
        Note that the cluster will pop right back again if its
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
        self.notifier.stop()
        self.eventer.stop()

    def _expunge(self, fsid):
        session = Session()
        session.query(SyncObject).filter_by(fsid=fsid).delete()
        session.commit()

    def _recover(self):
        session = Session()
        for server in session.query(Server).all():
            log.debug("Recovered server %s" % server.fqdn)
            # postgres stores dates in UTC, just set the timezone to tzutc() to get
            # a valid tz aware datetime out.
            last_contact = server.last_contact.replace(tzinfo=tzutc()) if server.last_contact else None
            self.servers.inject_server(ServerState(
                fqdn=server.fqdn,
                hostname=server.hostname,
                managed=server.managed,
                last_contact=last_contact
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
        fsids = [row[0] for row in session.query(SyncObject.fsid).distinct(SyncObject.fsid)]
        for fsid in fsids:
            cluster_monitor = ClusterMonitor(fsid, 'ceph', self.notifier, self.persister, self.servers, self.eventer)
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

                cluster_monitor.inject_sync_object(None, sync_type, version, json.loads(latest_record.data))

        for monitor in self.clusters.values():
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
        self.notifier.start()
        self.persister.start()
        self.eventer.start()

        self.servers.start()

    def join(self):
        log.info("%s joining" % self.__class__.__name__)
        self._rpc_thread.join()
        self._discovery_thread.join()
        self.notifier.join()
        self.persister.join()
        self.eventer.join()
        self.servers.join()
        for monitor in self.clusters.values():
            monitor.join()

    def on_discovery(self, minion_id, heartbeat_data):
        log.info("on_discovery: {0}/{1}".format(minion_id, heartbeat_data['fsid']))
        cluster_monitor = ClusterMonitor(heartbeat_data['fsid'], heartbeat_data['name'],
                                         self.notifier, self.persister, self.servers, self.eventer)
        self.clusters[heartbeat_data['fsid']] = cluster_monitor

        # Run before passing on the heartbeat, because otherwise the
        # syncs resulting from the heartbeat might not be received
        # by the monitor.
        cluster_monitor.start()
        cluster_monitor.on_heartbeat(minion_id, heartbeat_data)


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
