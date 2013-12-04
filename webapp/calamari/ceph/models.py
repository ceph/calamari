from django.utils import dateformat
from django.db import models
import jsonfield



class Cluster(models.Model):
    """
    A cluster being tracked by Calamari.
    """
    name = models.CharField(max_length=256, unique=True)
    api_base_url = models.CharField(max_length=200)

    # last time kraken ran
    cluster_update_attempt_time = models.DateTimeField(blank=True, null=True)

    # last time kraken successfully updated this cluster
    cluster_update_time = models.DateTimeField(blank=True, null=True)

    # message regarding the last error that occured (e.g. an exception stack
    # trace). This is cleared after any successful update.
    cluster_update_error_msg = models.TextField(blank=True, null=True)

    # true if the last kraken error occurred while communicating with the
    # cluster REST api.
    cluster_update_error_isclient = models.NullBooleanField(blank=True, null=True)

    #
    # Cluster state ready to be served up by the Calamari API.
    # 
    # These fields are populated by Kraken by performing any conversions from
    # the raw form, and as a side effect, validate the input.  Note that we
    # could store the raw data, but we'd rather throw an error at the Kraken
    # level if raw data is malformed and have stale data in the DB, than risk
    # having a cascading effect of problems with different components
    # expecting a certain schema if we were to blindly serve the raw data. We
    # can also choose to store the raw data, but this particular model seems
    # to maximize the decoupling between the particular web-framework being
    # used, and the extraction of knowledge from the cluster API. All of this
    # will probably be deleted and rewritten in the near future any way :).
    #
    space = jsonfield.JSONField(null=True)
    health = jsonfield.JSONField(null=True)
    osds = jsonfield.JSONField(null=True)
    osds_by_pg_state = jsonfield.JSONField(null=True)
    counters = jsonfield.JSONField(null=True)
    pgs = jsonfield.JSONField(null=True)

    def __unicode__(self):
        return self.name

    def _convert_to_unix_ms(self, t):
        if t is None:
            return None
        return int(dateformat.format(t, 'U')) * 1000

    def _get_cluster_update_time_ms(self):
        "Convert `cluster_update_time` into Unix time."
        return self._convert_to_unix_ms(self.cluster_update_time)

    def _get_cluster_update_attempt_time_ms(self):
        "Convert `cluster_update_attempt_time` into Unix time."
        return self._convert_to_unix_ms(self.cluster_update_attempt_time)

    cluster_update_time_unix = property(_get_cluster_update_time_ms)
    cluster_update_attempt_time_unix = property(_get_cluster_update_attempt_time_ms)

    def get_osd(self, osd_id):
        if not self.osds:
            return None
        for osd in self.osds:
            if osd['id'] == int(osd_id):
                return osd
        return None

    def has_osd(self, osd_id):
        return self.get_osd(osd_id) is not None


class Pool(models.Model):
    """
    This functionality was retrofitted to Calamari 1.x, which does not have south.
    To avoid adding a dependency for this one piece of data, simply create a new table
    instead of adding to Cluster, as plain django syncdb can handle new tables.
    """
    class Meta:
        unique_together = (('cluster', 'pool_id'),)

    cluster = models.ForeignKey(Cluster)
    pool_id = models.IntegerField()
    name = models.TextField()
    quota_max_bytes = models.BigIntegerField()
    quota_max_objects = models.BigIntegerField()
    used_objects = models.BigIntegerField()
    used_bytes = models.BigIntegerField()


class Server(models.Model):
    """
    Store what we know about the status of a server.

    In Calamari 1.x our resolution of hostnames/IPs is not robust, because
    we are not in contact with all the hosts to gather a full mapping of
    IPs to hostnames.

    The reliable data we have are:

    - The 'addr' field from the monmap for mons
    - The 'public_addr' field from the osdmap for OSDs

    The fuzzy data we have are:

    - Reverse DNS on the addresses, which may or may not provide any info
    - The mon IDs, which may be the hostnames if the cluster was set up
      with ceph-deploy
    - The CRUSH map, which may include a 'host' element type as an ancestor
      of an 'osd' element type, where the ID of the 'host' element is
      the hostname.

    Because we may or may not have a hostname (which may or may not be correct),
    the frontend network IP addresses are used as the ID here.  That's a pretty
    terrible ID, but it works as long as we're within one cluster.
    """

    class Meta:
        unique_together = (("addr", "cluster"),)

    cluster = models.ForeignKey(Cluster)

    addr = models.TextField()

    # Hostname, may be guessed from CRUSH map or reverse DNS
    hostname = models.TextField(null=True, blank=True)

    # Pretty name, may be set from hostname or mon ID
    name = models.TextField(null=True)


class ServiceStatus(models.Model):
    """
    Status of a RADOS service (mon or OSD).

    Use this to learn about which services are running on, or
    were last seen running on, a particular server in a cluster.
    """
    MON = 'mon'
    OSD = 'osd'

    class Meta:
        unique_together = (("server", "type", "service_id"),)

    # The server where we last saw this service (servers
    server = models.ForeignKey(Server)

    # OSD or MON?
    type = models.CharField(max_length='3')

    # OSD ID or mon rank
    service_id = models.IntegerField()

    # Human readable name (for mon it is mon.<name>, for OSD it is osd.<service_id>)
    name = models.TextField()
