
"""
Store and retrieve a FIFO buffer of recent versions of
synchronized objects (cluster maps etc)
"""
import json

import gevent.queue
import gevent.greenlet
import gevent.event

from sqlalchemy import Column, String, Text, DateTime, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from cthulhu.log import log


Base = declarative_base()
Session = sessionmaker()


class SyncObject(Base):
    __tablename__ = 'cthulhu_sync_object'

    # TODO: composite PK
    fsid = Column(Text, primary_key=True)
    sync_type = Column(String, primary_key=True)
    version = Column(Integer, nullable=True, primary_key=True)
    when = Column(DateTime)
    data = Column(Text)

    def __repr__(self):
        return "<SyncObject %s/%s/%s>" % (self.fsid, self.sync_type, self.version if self.version else self.when)

def initialize(db_path):
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)


class Persister(gevent.greenlet.Greenlet):
    """
    Asynchronously persist a queue of SyncObject updates to a
    database.
    """
    def __init__(self):
        super(Persister, self).__init__()

        self._queue = gevent.queue.Queue()
        self._complete = gevent.event.Event()

        self._session = Session()

    def update(self, fsid, sync_type, version, when, data):
        self._queue.put(SyncObject(
            fsid=fsid, sync_type=sync_type, version=version, when=when, data=json.dumps(data)
        ))

    def _run(self):
        while not self._complete.is_set():
            try:
                data = self._queue.get(block=True, timeout=1)
            except gevent.queue.Empty:
                continue
            else:
                try:
                    self._session.add(data)
                    self._session.commit()
                except Exception as e:
                    # Catch-all because all kinds of things can go wrong and our
                    # behaviour is the same: log the exception, the data that
                    # caused it, then try to go back to functioning.
                    log.error("Exception %s persisting data: %s" % (e, data))

    def stop(self):
        self._complete.set()
