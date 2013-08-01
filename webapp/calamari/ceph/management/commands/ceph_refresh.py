import traceback
from collections import defaultdict
from itertools import imap
import requests
from django.core.management.base import BaseCommand
from django.core.cache import cache
from ceph.models import Cluster

class CephRestClient(object):
    """
    Wrapper around the Ceph RESTful API.

    TODO: add a basic memoization decorator so we don't make multiple round
    trips for method below that result on the same Ceph cluster API endpoint.
    """
    def __init__(self, url):
        self.__url = url
        if self.__url[-1] != '/':
            self.__url += '/'

    def _query(self, endpoint):
        "Interrogate a Ceph API endpoint"
        hdr = {'accept': 'application/json'}
        r = requests.get(self.__url + endpoint, headers = hdr)
        return r.json()

    def get_status(self):
        "Get the raw `ceph status` output"
        return self._query("status")["output"]

    def get_space_stats(self):
        "Get the raw `ceph df` output"
        return self._query("df")["output"]

    def get_health(self):
        "Get the raw `ceph health detail` output"
        return self._query("health?detail")["output"]

    def get_osds(self):
        "Get the raw `ceph osd dump` output"
        return self._query("osd/dump")["output"]

    def get_pg_pools(self):
        "Get the raw `ceph pg/dump?dumpcontents=pools` output"
        return self._query("pg/dump?dumpcontents=pools")["output"]

class ModelAdapter(object):
    CRIT_STATES = set(['stale', 'down', 'peering', 'inconsistent', 'incomplete'])
    WARN_STATES = set(['creating', 'recovery_wait', 'recovering', 'replay',
            'splitting', 'degraded', 'remapped', 'scrubbing', 'repair',
            'wait_backfill', 'backfilling', 'backfill_toofull'])
    OKAY_STATES = set(['active', 'clean'])

    def __init__(self, client, cluster):
        self.client = client
        self.cluster = cluster

    def refresh(self):
        "Call each _populate* method, then save the model instance"
        attrs = filter(lambda a: a.startswith('_populate_'), dir(self))
        for attr in attrs:
            getattr(self, attr)()
        self.cluster.save()

    def _populate_space(self):
        "Fill in the cluster space statistics"
        data = self.client.get_space_stats()['stats']
        self.cluster.space = {
            'used_bytes': data['total_used'] * 1024,
            'capacity_bytes': data['total_space'] * 1024,
            'free_bytes': data['total_avail'] * 1024,
        }

    def _populate_health(self):
        "Fill in the cluster health state"
        data = self.client.get_health()
        self.cluster.health = {
            'overall_status': data['overall_status'],
            'detail': data['detail'],
            'summary': data['summary'],
        }

    def _populate_osds(self):
        "Fill in the set of cluster OSDs"
        data = self.client.get_osds()
        self.cluster.osds = data["osds"]

    def _populate_counters(self):
        self.cluster.counters = {
            'pool': self._calculate_pool_counters(),
            'osd': self._calculate_osd_counters(),
            'mds': self._calculate_mds_counters(),
            'mon': self._calculate_mon_counters(),
            'pg': self._calculate_pg_counters(),
        }

    def _calculate_pool_counters(self):
        fields = ['num_objects_unfound', 'num_objects_missing_on_primary',
            'num_deep_scrub_errors', 'num_shallow_scrub_errors',
            'num_scrub_errors', 'num_objects_degraded']
        counts = defaultdict(lambda: 0)
        pools = self.client.get_pg_pools()
        for pool in imap(lambda p: p['stat_sum'], pools):
            for key, value in pool.items():
                counts[key] += min(value, 1)
        for delkey in set(counts.keys()) - set(fields):
            del counts[delkey]
        counts['total'] = len(pools)
        return counts

    def _calculate_osd_counters(self):
        osds = self.client.get_status()['osdmap']['osdmap']
        keys = ['num_osds', 'num_up_osds', 'num_in_osds']
        total, up, inn = (int(osds[k]) for k in keys)
        return {
            'total': total,
            'up_in': inn,
            'up_not_in': up-inn,
            'not_up_not_in': total-up,
        }

    def _calculate_mds_counters(self):
        mdsmap = self.client.get_status()['mdsmap']
        total = mdsmap['max']
        up = mdsmap['up']
        inn = mdsmap['in']
        return {
            'total': total,
            'up_in': inn,
            'up_not_in': up-inn,
            'not_up_not_in': total-up,
        }

    def _calculate_mon_counters(self):
        status = self.client.get_status()
        mons = len(status['monmap']['mons'])
        quorum = len(status['quorum'])
        return {
            'total': mons,
            'in_quorum': quorum,
            'not_in_quorum': mons-quorum,
        }

    def _calculate_pg_counters(self):
        pg_map = self.client.get_status()['pgmap']
        ok, warn, crit = 0, 0, 0
        for pg_state in pg_map['pgs_by_state']:
            count = pg_state['count']
            states = map(lambda s: s.lower(), pg_state['state_name'].split("+"))
            if len(self.CRIT_STATES.intersection(states)) > 0:
                crit += count
            elif len(self.WARN_STATES.intersection(states)) > 0:
                warn += count
            elif len(self.OKAY_STATES.intersection(states)) > 0:
                ok += count
        return {
            'total': pg_map['num_pgs'],
            'ok': ok,
            'warn': warn,
            'critical': crit,
        }

class Command(BaseCommand):
    """
    Administrative function for refreshing Ceph cluster stats.

    The `ceph_refresh` command will attempt to update statistics for each
    registered cluster found in the database.

    A failure that occurs while updating cluster statistics will abort the
    refresh for that cluster. An attempt will be made for other clusters.
    """
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self._last_response = None    # last cluster query response

    def _handle_cluster(self, cluster):
        self.stdout.write("Refreshing data from cluster: %s (%s)" % \
                (cluster.name, cluster.api_base_url))
        client = CephRestClient(cluster.api_base_url)
        adapter = ModelAdapter(client, cluster)
        adapter.refresh()

    def handle(self, *args, **options):
        """
        Update statistics for each registered cluster.
        """
        clusters = Cluster.objects.all()
        self.stdout.write("Updating %d clusters..." % (len(clusters),))
        for cluster in clusters:
            try:
                self._handle_cluster(cluster)
            except Exception:
                self.stderr.write(traceback.format_exc())
        cache.clear()
        self.stdout.write("Update completed!")

#
# This is the algorithm I was using to send the UI OSD Map deltas. We aren't
# keeping history now, so it isn't needed. It's here for later reference.
#
#def delta(self, other):
#    """
#    Compute a delta between the OSD lists of `self` and `other`.
#
#    An OSD in self.osds will appear in output `new` if it not in
#    other.osds. The opposite is true for output `removed`. The output
#    `changed` is determined by an OSD equality operation that performs a
#    simple single-level dictionary comparison.
#
#    Return:
#      (new, removed, changed)
#    """
#    def compare_osd(a, b):
#        "Simple single-level dictionary comparison."
#        if set(a.keys()) != set(b.keys()):
#            return False
#        for key, value in a.items():
#            if b[key] != value:
#                return False
#        return True
#
#    # look-up table mapping id to osd
#    other_ids = dict((osd['osd'], osd) for osd in other.osds)
#
#    # generate the delta
#    new, changed = [], []
#    for osd in self.osds:
#        osd_id = osd['osd']
#        if osd_id in other_ids:
#            if not compare_osd(osd, other_ids[osd_id]):
#                changed.append(osd)
#            del other_ids[osd_id]
#        else:
#            new.append(osd)
#
#    # new, removed, changed
#    return new, other_ids.values(), changed
