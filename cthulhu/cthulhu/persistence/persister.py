

from collections import namedtuple
import logging
import datetime
from calamari_common.db.event import Event

import gevent.greenlet
import gevent.queue
import gevent.event

try:
    import msgpack
except ImportError:
    msgpack = None

from sqlalchemy.orm import sessionmaker
from cthulhu.manager import config

from cthulhu.persistence.sync_objects import SyncObject
from cthulhu.persistence.servers import Server, Service

from cthulhu.util import now
from cthulhu.log import log

Session = sessionmaker()

DeferredCall = namedtuple('DeferredCall', ['fn', 'args', 'kwargs'])


CLUSTER_MAP_RETENTION = datetime.timedelta(seconds=int(config.get('cthulhu', 'cluster_map_retention')))


class Persister(gevent.greenlet.Greenlet):
    """
    Asynchronously persist a queue of updates.  This is for use by classes
    that maintain the primary copy of state in memory, but also lazily update
    the DB so that they can recover from it on restart.
    """
    def __init__(self):
        super(Persister, self).__init__()

        self._queue = gevent.queue.Queue()
        self._complete = gevent.event.Event()

        self._session = Session()

        # Plumb the sqlalchemy logger into our cthulhu logger's output
        logging.getLogger('sqlalchemy.engine').setLevel(logging.getLevelName(config.get('cthulhu', 'db_log_level')))
        for handler in log.handlers:
            logging.getLogger('sqlalchemy.engine').addHandler(handler)

    def __getattribute__(self, item):
        """
        Wrap functions with logging
        """
        if item.startswith('_'):
            return object.__getattribute__(self, item)
        else:
            try:
                return object.__getattribute__(self, item)
            except AttributeError:
                try:
                    attr = object.__getattribute__(self, "_%s" % item)
                    if callable(attr):
                        def defer(*args, **kwargs):
                            dc = DeferredCall(attr, args, kwargs)
                            self._queue.put(dc)
                        return defer
                    else:
                        return object.__getattribute__(self, item)
                except AttributeError:
                    return object.__getattribute__(self, item)

    def _update_sync_object(self, fsid, name, sync_type, version, when, data):
        self._session.add(SyncObject(fsid=fsid, cluster_name=name, sync_type=sync_type, version=version, when=when,
                                     data=msgpack.packb(data)))

        # Time-limited FIFO
        threshold = now() - CLUSTER_MAP_RETENTION
        self._session.query(SyncObject).filter(
            SyncObject.when < threshold,
            SyncObject.fsid == fsid,
            SyncObject.sync_type == sync_type).delete()

    def _create_server(self, *args, **kwargs):
        self._session.add(Server(*args, **kwargs))

    def _update_server(self, update_fqdn, **attrs):
        self._session.query(Server).filter_by(fqdn=update_fqdn).update(attrs)

    def _create_service(self, associate_fqdn, *args, **kwargs):
        service = Service(*args, **kwargs)
        self._session.add(service)
        service.server = self._session.query(Server).filter_by(fqdn=associate_fqdn).one().id

    def _update_service(self, service_id, **attrs):
        self._session.query(Service).filter_by(
            fsid=service_id.fsid,
            service_type=service_id.service_type,
            service_id=service_id.service_id
        ).update(attrs)

    def _update_service_location(self, service_id, location_fqdn):
        self._session.query(Service).filter_by(
            fsid=service_id.fsid,
            service_type=service_id.service_type,
            service_id=service_id.service_id
        ).update({'server': self._session.query(Server).filter_by(fqdn=location_fqdn).one().id})

    def _delete_service(self, service_id):
        self._session.query(Service).filter_by(
            fsid=service_id.fsid,
            service_type=service_id.service_type,
            service_id=service_id.service_id
        ).delete()

    def _delete_server(self, fqdn):
        self._session.query(Server).filter_by(fqdn=fqdn).delete()

    def _save_events(self, events):
        for event in events:
            self._session.add(Event(
                severity=event.severity,
                message=event.message,
                when=event.when,
                **event.associations))

    def _run(self):
        log.info("Persister listening")

        while not self._complete.is_set():
            try:
                data = self._queue.get(block=True, timeout=1)
            except gevent.queue.Empty:
                continue
            else:
                try:
                    data.fn(*data.args, **data.kwargs)
                    self._session.commit()
                except Exception:
                    # Catch-all because all kinds of things can go wrong and our
                    # behaviour is the same: log the exception, the data that
                    # caused it, then try to go back to functioning.
                    log.exception("Persister exception persisting data: %s" % (data.fn,))

                    self._session.rollback()

    def stop(self):
        self._complete.set()
