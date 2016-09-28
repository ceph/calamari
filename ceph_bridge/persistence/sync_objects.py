from etcdobj import EtcdObj
from etcdobj import fields


class SyncObject(EtcdObj):
    """A table for storing a FIFO of ClusterMonitor 'sync objects', i.e.

    cluster maps.

    """
    __name__ = 'raw/ceph/%s/maps/%s'

    fsid = fields.StrField("fsid")
    cluster_name = fields.StrField("cluster_name")
    sync_type = fields.StrField("sync_type")
    version = fields.StrField("version")
    when = fields.StrField("when")
    data = fields.StrField("data")
    updated = fields.StrField("updated")

    def render(self):
        self.__name__ = self.__name__ % (self.fsid, self.sync_type)
        return super(SyncObject, self).render()
