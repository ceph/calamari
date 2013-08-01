from collections import defaultdict
from django.utils import dateformat
from django.db import models
import jsonfield

class Cluster(models.Model):
    """
    A cluster being tracked by Calamari.
    """
    name = models.CharField(max_length=256)
    last_update = models.DateTimeField(auto_now=True)
    api_base_url = models.CharField(max_length=200)

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
    counters = jsonfield.JSONField(null=True)

    def __unicode__(self):
        return self.name

    def _get_last_update_ms(self):
        "Convert `last_update` into Unix time."
        return int(dateformat.format(self.last_update, 'U')) * 1000

    last_update_unix = property(_get_last_update_ms)

    def get_osd(self, osd_id):
        if not self.osds:
            return None
        for osd in self.osds:
            if osd['osd'] == int(osd_id):
                return osd
        return None

    def has_osd(self, osd_id):
        return self.get_osd(osd_id) is not None

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

class ClusterStatus(Dump):
    """
    A snapshot of cluster status.
    """
    CRIT_STATES = set(['stale', 'down', 'peering', 'inconsistent', 'incomplete'])
    WARN_STATES = set(['creating', 'recovery_wait', 'recovering', 'replay',
            'splitting', 'degraded', 'remapped', 'scrubbing', 'repair',
            'wait_backfill', 'backfilling', 'backfill_toofull'])
    OKAY_STATES = set(['active', 'clean'])

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

    def osd_count_by_status(self):
        """
        Number of OSDs categorized by status.

        Return:
          (total, up&in, up&!in, !up&!in)
        """
        osds = self.report['osdmap']['osdmap']
        keys = ['num_osds', 'num_up_osds', 'num_in_osds']
        total, up, inn = (int(osds[k]) for k in keys)
        # inn implies up (and includes up count)
        return total, inn, up-inn, total-up

    def mon_count_by_status(self):
        mons = len(self.report['monmap']['mons'])
        quorum = len(self.report['quorum'])
        return mons, quorum, mons-quorum

    def pg_count_by_status(self):
        ok, warn, crit = 0, 0, 0
        pg_map = self.report['pgmap']
        for pg_state in pg_map['pgs_by_state']:
            count = pg_state['count']
            states = map(lambda s: s.lower(), pg_state['state_name'].split("+"))
            if len(self.CRIT_STATES.intersection(states)) > 0:
                crit += count
            elif len(self.WARN_STATES.intersection(states)) > 0:
                warn += count
            elif len(self.OKAY_STATES.intersection(states)) > 0:
                ok += count
        return pg_map['num_pgs'], ok, warn, crit


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

class PGPoolDump(Dump):
    """
    A pg pools dump snapshot.
    """
    pass
