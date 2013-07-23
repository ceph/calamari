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

class ClusterStatus(Dump):
    """
    A snapshot of cluster status.
    """
    pass

    def mds_count_by_status(self):
        """
        Number of MDSs categorized by status.

        Return:
          (total, up&in, up&!in, !up&!in)
        """
        total = self.report['mdsmap']['max']
        up = self.report['mdsmap']['up']
        inn = self.report['mdsmap']['in']
        # inn implies up (and includes up count)
        return total, inn, up-inn, total-up

class OSDDump(Dump):
    """
    Snapshot of the state of object storage devices.
    """

    def delta(self, other):
        """
        Compute a delta between the OSD lists of `self` and `other`.

        An OSD in self.osds will appear in output `new` if it not in
        other.osds. The opposite is true for output `removed`. The output
        `changed` is determined by an OSD equality operation that performs a
        simple single-level dictionary comparison.

        Return:
          (new, removed, changed)
        """
        def compare_osd(a, b):
            "Simple single-level dictionary comparison."
            if set(a.keys()) != set(b.keys()):
                return False
            for key, value in a.items():
                if b[key] != value:
                    return False
            return True

        # look-up table mapping id to osd
        other_ids = dict((osd['osd'], osd) for osd in other.osds)

        # generate the delta
        new, changed = [], []
        for osd in self.osds:
            osd_id = osd['osd']
            if osd_id in other_ids:
                if not compare_osd(osd, other_ids[osd_id]):
                    changed.append(osd)
                del other_ids[osd_id]
            else:
                new.append(osd)

        # new, removed, changed
        return new, other_ids.values(), changed

    def get_osd(self, id):
        "Find a specific OSD in the raw dump"
        for osd in self.osds:
            if osd['osd'] == int(id):
                return osd
        return None

    def _get_osds(self):
        "Select the OSD list from the raw JSON"
        return self.report['osds']

    osds = property(_get_osds)

    def _get_num_osds(self):
        """
        Count OSDs by up/in status.

        Return:
          (total, up&in, up&!in, !up&!in)
        """
        cnts = defaultdict(lambda: 0)
        for osd in self.osds:
            up, inn = bool(osd['up']), bool(osd['in'])
            cnts[(up, inn)] += 1
        return (len(self.osds), cnts[(True, True)], \
                cnts[(True, False)], cnts[(False, False)])

    num_osds = property(_get_num_osds)

class PGPoolDump(Dump):
    """
    A pg pools dump snapshot.
    """
    pass
