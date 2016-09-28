from etcdobj import EtcdObj
from etcdobj import fields


class Server(EtcdObj):
    """A table of the servers seen by ServerMonitor, lazily updated

    """
    __name__ = 'raw/ceph/%s/servers/%s'

    fsid = fields.StrField("fsid")
    # use fqdn as unique identifier
    fqdn = fields.StrField("fqdn")
    hostname = fields.StrField("hostname")
    managed = fields.StrField("managed")
    last_contact = fields.StrField("last_contact")
    boot_time = fields.StrField("boot_time")
    ceph_version = fields.StrField("ceph_version")

    def render(self):
        self.__name__ = self.__name__ % (self.fsid, self.fqdn)
        return super(Server, self).render()


class Service(EtcdObj):
    """A table of the ceph services seen by ServerMonitor, usually

    each one is associated with a Server, lazily updated.

    """
    __name__ = 'raw/ceph/%s/services/%s/%s/%s'

    fsid = fields.StrField("fsid")
    service_type = fields.StrField("service_type")
    # mon name or OSD id (as string)
    service_id = fields.StrField("service_id")
    # Whether the service process is running
    running = fields.StrField("running")
    # Any status metadata (mon_status) reported, as json string
    status = fields.StrField("status")

    # Server uuid
    server_uuid = fields.StrField("server_uuid")
    server_fqdn = fields.StrField("server_fqdn")

    def render(self):
        self.__name__ = self.__name__ % (
            self.fsid, self.server_fqdn, self.service_type, self.service_id)
        return super(Service, self).render()
