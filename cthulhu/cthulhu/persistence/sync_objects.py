

from sqlalchemy import Column, String, Text, DateTime, Integer, LargeBinary
from calamari_common.db.base import Base


class SyncObject(Base):
    """
    A table for storing a FIFO of ClusterMonitor 'sync objects', i.e.
    cluster maps.
    """
    __tablename__ = 'cthulhu_sync_object'

    # TODO: composite PK
    fsid = Column(Text, primary_key=True)
    cluster_name = Column(Text)  # FIXME this is denormalized because currently there isn't a cluster table
    sync_type = Column(String, primary_key=True)
    version = Column(Integer, nullable=True, primary_key=True)
    when = Column(DateTime, index=True)
    data = Column(LargeBinary)

    def __repr__(self):
        return "<SyncObject %s/%s/%s>" % (self.fsid, self.sync_type, self.version if self.version else self.when)
