

from sqlalchemy import Column, Text, Integer, ForeignKey, Boolean, DateTime
from cthulhu.persistence import Base


class Server(Base):
    """
    A table of the servers seen by ServerMonitor, lazily updated
    """
    __tablename__ = 'cthulhu_server'

    id = Column(Integer, autoincrement=True, primary_key=True)

    # FQDN is not primary key because it can change if a server
    # was previously known to use by hostname and subsequently
    # it becomes known to use by full FQDN.
    fqdn = Column(Text, primary_key=False)
    hostname = Column(Text)
    managed = Column(Boolean)
    last_contact = Column(DateTime(timezone=True))

    def __repr__(self):
        return "<Server %s>" % self.fqdn


class Service(Base):
    """
    A table of the ceph services seen by ServerMonitor, usually
    each one is associated with a Server, lazily updated.
    """
    __tablename__ = 'cthulhu_server_service'

    fsid = Column(Text, primary_key=True)
    service_type = Column(Text, primary_key=True)
    service_id = Column(Text, primary_key=True)

    server = Column(Integer, ForeignKey("cthulhu_server.id"), nullable=True)
