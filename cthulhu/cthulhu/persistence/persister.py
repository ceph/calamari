

import json
from collections import namedtuple
import logging

import gevent.greenlet
import gevent.queue

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cthulhu.persistence import Base
from cthulhu.persistence.servers import Server, Service
from cthulhu.persistence.sync_objects import SyncObject
from cthulhu.log import log

Session = sessionmaker()


def initialize(db_path):
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)


DeferredCall = namedtuple('DeferredCall', ['fn', 'args', 'kwargs'])


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

        if log.level <= logging.DEBUG:
            logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
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
                            log.debug("Persister deferring >> %s(%s, %s)" % (item, args, kwargs))
                            self._queue.put(dc)
                        return defer
                    else:
                        return object.__getattribute__(self, item)
                except AttributeError:
                    return object.__getattribute__(self, item)

    def _update_sync_object(self, fsid, sync_type, version, when, data):
        # TODO: FIFO logic with count limit
        self._session.add(SyncObject(fsid=fsid, sync_type=sync_type, version=version, when=when, data=json.dumps(data)))

    def _create_server(self, server):
        self._session.add(server)

    def _update_server(self, update_fqdn, **attrs):
        self._session.query(Server).filter_by(fqdn=update_fqdn).update(attrs)

    def _create_service(self, service, associate_fqdn=None):
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
        ).update(server=self._session.query(Server).filter_by(fqdn=location_fqdn).one().id)

    def _delete_service(self, service_id):
        self._session.query(Service).filter_by(
            fsid=service_id.fsid,
            service_type=service_id.service_type,
            service_id=service_id.service_id
        ).delete()

    def _delete_server(self, fqdn):
        self._session.query(Server).filter_by(fqdn=fqdn).delete()

    def _run(self):
        log.info("Persister listening")

        while not self._complete.is_set():
            try:
                data = self._queue.get(block=True, timeout=1)
            except gevent.queue.Empty:
                continue
            else:
                try:
                    log.debug("Persister executing >> %s(%s, %s)" % (
                        data.fn.__name__, data.args, data.kwargs))
                    data.fn(*data.args, **data.kwargs)
                    self._session.commit()
                except Exception:
                    # Catch-all because all kinds of things can go wrong and our
                    # behaviour is the same: log the exception, the data that
                    # caused it, then try to go back to functioning.
                    log.exception("Persister exception persisting data: %s" % (data,))

                    self._session.rollback()

    def stop(self):
        self._complete.set()
