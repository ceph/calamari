from collections import defaultdict
from django.utils import dateformat
from django.db import models
import jsonfield

class Cluster(models.Model):
    """
    A cluster being tracked by Calamari.
    """
    name = models.CharField(max_length=256)

    # REST API URL (e.g. monitor:port/api/v0.1)
    api_base_url = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class DumpManager(models.Manager):
    def for_cluster(self, cluster_pk):
        "Filter queryset by cluster primary-key"
        return self.get_query_set().filter(cluster__pk=cluster_pk)

class Dump(models.Model):
    """
    Base class for JSON snapshots retrieved from querying a cluster.
    Subclasses may pre-process a raw dump to record derived data.

    Each dump originates from a specific `cluster`. The `added` field records
    the time the record was inserted into the database, and is used to
    calculate the age/freshness of data. The `report` field stores the JSON
    dump, and is automagically serialized/deserialized.
    """
    cluster = models.ForeignKey(Cluster)
    added = models.DateTimeField(auto_now_add=True)
    report = jsonfield.JSONField()

    objects = DumpManager()

    class Meta:
        abstract = True
        get_latest_by = "added"

    def _get_added_ms(self):
        "Convert `added` into Unix time."
        return int(dateformat.format(self.added, 'U')) * 1000

    added_ms = property(_get_added_ms)

class ClusterSpace(Dump):
    """
    A snapshot of cluster space statistics.

    This roughly corresponds to `ceph df` without the per-pool statistics.
    """
    pass

class ClusterHealth(Dump):
    """
    A snapshot of cluster health.
    """
    pass

class OSDDump(Dump):
    """
    Snapshot of the state of object storage devices.
    """
    def _get_num_osds(self):
        """
        Count OSDs by up/in status.

        Return:
          (total, up&in, up&!in, !up&!in)
        """
        cnts = defaultdict(lambda: 0)
        osds = self.report['osds']
        for osd in osds:
            up, inn = bool(osd['up']), bool(osd['in'])
            cnts[(up, inn)] += 1
        return (len(osds), cnts[(True, True)], \
                cnts[(True, False)], cnts[(False, False)])

    num_osds = property(_get_num_osds)

class PGPoolDump(Dump):
    """
    A pg pools dump snapshot.
    """
    pass
