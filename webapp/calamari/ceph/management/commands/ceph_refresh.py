import traceback
from optparse import make_option
from collections import defaultdict
from itertools import imap
import re
import requests
import socket
from django.core.management.base import BaseCommand
from django.utils.timezone import utc
from datetime import datetime
from ceph.models import Cluster

# Addresses to ignore during monitor ping test
_MON_ADDR_IGNORES = ("0.0.0.0", "0:0:0:0:0:0:0:0", "::")

# Default timeout for communicating with the Ceph REST API.
_REST_CLIENT_DEFAULT_TIMEOUT = 10.0

def memoize(function):
    memo = {}
    def wrapper(*args):
        if args in memo:
            return memo[args]
        else:
            rv = function(*args)
            memo[args] = rv
            return rv
    return wrapper	

class CephRestClient(object):
    """
    Wrapper around the Ceph RESTful API.

    The memoize decorator on the _query method is used to avoid making the same
    round-trip to the rest server. This shouldn't be used if it is important
    that values can change during the execution of this program, as this
    effectively adds a cache that is never cleared.
    """
    def __init__(self, url, timeout=_REST_CLIENT_DEFAULT_TIMEOUT):
        self.__url = url
        if self.__url[-1] != '/':
            self.__url += '/'
        self.timeout = timeout

    @memoize
    def _query(self, endpoint):
        "Interrogate a Ceph API endpoint"
        hdr = {'accept': 'application/json'}
        r = requests.get(self.__url + endpoint,
                headers = hdr, timeout=self.timeout)
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

    def get_pools(self):
        "Get the raw `ceph osd lspools` output"
        return self._query("osd/lspools")["output"]

    def get_pg_dump(self):
        "Get the raw `ceph pg dump` output"
        return self._query("pg/dump")["output"]

    def get_pg_stats(self, brief=True):
        "Get the pg stats"
        if brief:
            return self._query("pg/dump?dumpcontents=pgs_brief")["output"]
        else:
            return self.get_pg_dump()['pg_stats']

    def get_osd_tree(self):
        "Get the raw `ceph osd tree` output"
        return self._query("osd/tree")["output"]

class ModelAdapter(object):
    CRIT_STATES = set(['stale', 'down', 'peering', 'inconsistent', 'incomplete'])
    WARN_STATES = set(['creating', 'recovery_wait', 'recovering', 'replay',
            'splitting', 'degraded', 'remapped', 'scrubbing', 'repair',
            'wait_backfill', 'backfilling', 'backfill_toofull'])
    OKAY_STATES = set(['active', 'clean'])

    OSD_FIELDS = ['uuid', 'up', 'in', 'up_from', 'public_addr',
            'cluster_addr', 'heartbeat_back_addr', 'heartbeat_front_addr']

    PG_FIELDS = ['pgid', 'acting', 'up', 'state']

    def __init__(self, client, cluster, mon_timeout):
        self.client = client
        self.cluster = cluster
        self.mon_timeout = mon_timeout

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

    def _populate_osds_and_pgs(self):
        "Fill in the PG and OSD lists"

        # map osd id to pg states
        pg_states_by_osd = defaultdict(lambda: defaultdict(lambda: 0))
        # map osd id to set of pools
        pools_by_osd = defaultdict(lambda: set([]))
        # map pg state to osd ids
        osds_by_pg_state = defaultdict(lambda: set([]))

        # helper to modify each pg object
        def fixup_pg(pg):
            data = dict((k, pg[k]) for k in self.PG_FIELDS)
            data['state'] = data['state'].split("+")
            return data

        # save the brief pg map
        pgs = self.client.get_pg_stats()
        self.cluster.pgs = map(fixup_pg, pgs)

        # get the list of pools
        pools = self.client.get_pools()
        pools_by_id = dict((d['poolnum'], d['poolname']) for d in pools)

        # populate the indexes
        for pg in self.cluster.pgs:
            pool_id = int(pg['pgid'].split(".")[0])
            acting = set(pg['acting'])
            for state in pg['state']:
                osds_by_pg_state[state] |= acting
                for osd_id in acting:
                    pg_states_by_osd[osd_id][state] += 1
                    if pools_by_id.has_key(pool_id):
                        pools_by_osd[osd_id] |= set([pools_by_id[pool_id]])

        # convert set() to list to make JSON happy
        osds_by_pg_state = dict((k, list(v)) for k, v in
                osds_by_pg_state.iteritems())
        self.cluster.osds_by_pg_state = osds_by_pg_state

        # get the osd tree. we'll use it to get hostnames
        osd_tree = self.client.get_osd_tree()
        nodes_by_id = dict((n["id"], n) for n in osd_tree["nodes"])

        # FIXME: this assumes that an osd node is a direct descendent of a
        #
        # host. It also assumes that these node types are called 'osd', and
        # 'host' respectively. This is probably not as general as we would like
        # it. Some clusters might have weird crush maps. This also assumes that
        # the host name in the crush map is the same host name reported by
        # Diamond. It is fragile.
        host_by_osd_name = defaultdict(lambda: None)
        for node in osd_tree["nodes"]:
            if node["type"] == "host":
                host = node["name"]
                for id in node["children"]:
                    child = nodes_by_id[id]
                    if child["type"] == "osd":
                        host_by_osd_name[child["name"]] = host

        # helper to modify each osd object
        def fixup_osd(osd):
            osd_id = osd['osd']
            data = dict((k, osd[k]) for k in self.OSD_FIELDS)
            data.update({'id': osd_id})
            data.update({'pg_states': pg_states_by_osd[osd_id]})
            data.update({'pools': list(pools_by_osd[osd_id])})
            data.update({'host': host_by_osd_name["osd.%d" % (osd_id,)]})
            return data

        # add the pg states to each osd
        osds = self.client.get_osds()["osds"]
        self.cluster.osds = map(fixup_osd, osds)

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
        osds = self.client.get_osds()["osds"]
        counters = {
            'total': len(osds),
            'not_up_not_in': 0,
            'not_up_in': 0,
            'up_not_in': 0,
            'up_in': 0
        }
        for osd in osds:
            up, inn = osd['up'], osd['in']
            if not up and not inn:
                counters['not_up_not_in'] += 1
            elif not up and inn:
                counters['not_up_in'] += 1
            elif up and not inn:
                counters['up_not_in'] += 1
            elif up and inn:
                counters['up_in'] += 1
        warn_count = counters['up_not_in'] + counters['not_up_in']
        warn_states = {}
        if counters['up_not_in'] > 0:
            warn_states['up/out'] = counters['up_not_in']
        if counters['not_up_in'] > 0:
            warn_states['down/in'] = counters['not_up_in']
        return {
            'ok': {
                'count': counters['up_in'],
                'states': {} if counters['up_in'] == 0 else {'up/in': counters['up_in']},
            },
            'warn': {
                'count': warn_count,
                'states': {} if warn_count == 0 else warn_states,
            },
            'critical': {
                'count': counters['not_up_not_in'],
                'states': {} if counters['not_up_not_in'] == 0 else {'down/out': counters['not_up_not_in']},
            },
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


    # very basic IPv4/6 formats based on the printf's that ceph does when
    # serializing an entity_addr_t.
    _IPV4_RE = r"(?P<addr>\d+\.\d+\.\d+\.\d+):(?P<port>\d+)\/"
    _IPV6_RE = r"\[(?P<addr>\S+)\]:(?P<port>\d+)\/"

    def try_mon_connect(self, mon):
        """Try to connect to the monitor.

        This attempts to establish a TCP connection to the monitor. Note that
        the connection attempt is blocking. If we are trying to connect to a
        large number of monitors and/or we would like a longer timeout, we may
        want to start this process in the background as soon as we begin a new
        cluster refresh attempt.
        """
        # parse the monitor address fields
        addr = mon['addr']
        m = re.match(self._IPV4_RE, addr)
        if not m:
            m = re.match(self._IPV6_RE, addr)

        sock = None
        try:
            # if we weren't able to parse the address this regex group
            # extraction will fail and we'll skip this monitor.
            addr, port = m.group("addr"), int(m.group("port"))
            # skip ignored addresses (e.g. 0.0.0.0, ::)
            # a future enhancement here is to use the python 'ipaddress'
            # library which contains routines for identifying addresses based
            # on properties such as 'unspecified', 'reserved', and 'multicast'.
            if addr in _MON_ADDR_IGNORES:
                return False
            sock = socket.create_connection((addr, port), timeout=self.mon_timeout)
            return True
        except Exception as e:
            return False
        finally:
            # the python documentation doesn't say whether or not sock.close()
            # will throw an exception, but we want to avoid marking a monitor
            # down in the case that we just had a hiccup closing the socket
            # connection.
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass

    def _calculate_mon_counters(self):
        status = self.client.get_status()
        mons = status['monmap']['mons']
        quorum = status['quorum']
        ok, warn, crit = 0, 0, 0
        for mon in mons:
            rank = mon['rank']
            if rank in quorum:
                ok += 1
            elif self.try_mon_connect(mon):
                warn += 1
            else:
                crit += 1
        return {
            'ok': {
                'count': ok,
                'states': {} if ok == 0 else {'in': ok},
            },
            'warn': {
                'count': warn,
                'states': {} if warn == 0 else {'up': warn},
            },
            'critical': {
                'count': crit,
                'states': {} if crit == 0 else {'out': crit},
            }
        }

    def _pg_counter_helper(self, states, classifier, count, stats):
        matched_states = classifier.intersection(states)
        if len(matched_states) > 0:
            stats[0] += count
            for state in matched_states:
                stats[1][state] += count
            return True
        return False

    def _calculate_pg_counters(self):
        pg_map = self.client.get_status()['pgmap']
        ok, warn, crit = [[0, defaultdict(int)] for _ in range(3)]
        for pg_state in pg_map['pgs_by_state']:
            count = pg_state['count']
            states = map(lambda s: s.lower(), pg_state['state_name'].split("+"))
            if self._pg_counter_helper(states, self.CRIT_STATES, count, crit):
                pass
            elif self._pg_counter_helper(states, self.WARN_STATES, count, warn):
                pass
            elif self._pg_counter_helper(states, self.OKAY_STATES, count, ok):
                pass
        return {
            'ok': {
                'count': ok[0],
                'states': ok[1],
            },
            'warn': {
                'count': warn[0],
                'states': warn[1],
            },
            'critical': {
                'count': crit[0],
                'states': crit[1],
            },
        }

class Command(BaseCommand):
    """
    Administrative function for refreshing Ceph cluster stats.

    The `ceph_refresh` command will attempt to update statistics for each
    registered cluster found in the database.

    A failure that occurs while updating cluster statistics will abort the
    refresh for that cluster. An attempt will be made for other clusters.
    """
    option_list = BaseCommand.option_list + (
        make_option('--restapi-timeout',
            action='store',
            type="float",
            dest='restapi_connect_timeout',
            default=30.0,
            help='Timeout (sec) to connect to cluster REST API'),
        make_option('--monitor-timeout',
            action='store',
            type="float",
            dest='monitor_connect_timeout',
            default=5.0,
            help='Timeout (sec) to connect to montior'),
        )
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self._last_response = None    # last cluster query response

    def _handle_cluster(self, cluster, options):
        self.stdout.write("Refreshing data from cluster: %s (%s)" % \
                (cluster.name, cluster.api_base_url))
        client = CephRestClient(cluster.api_base_url,
                options['restapi_connect_timeout'])
        adapter = ModelAdapter(client, cluster,
                options['monitor_connect_timeout'])
        adapter.refresh()

    def handle(self, *args, **options):
        """
        Update statistics for each registered cluster.
        """
        clusters = Cluster.objects.all()
        self.stdout.write("Updating %d clusters..." % (len(clusters),))
        for cluster in clusters:
            now = datetime.utcnow().replace(tzinfo=utc)

            # reset error fields, cross fingers for success!
            cluster.cluster_update_error_isclient = False
            cluster.cluster_update_error_msg = None

            try:
                self._handle_cluster(cluster, options)
                # record time of last successsful update
                cluster.cluster_update_time = now
            except Exception as e:
                # Check base class of all errors generated in the Requests
                # framework. We use that property to indicate the error
                # occurred trying to communicate with the cluster RESTApi.
                if isinstance(e, requests.exceptions.RequestException):
                    cluster.cluster_update_error_isclient = True
                error = traceback.format_exc()
                self.stdout.flush()
                self.stderr.write(error)
                cluster.cluster_update_error_msg = error

            # try to save the changes and note the time. if we cannot record
            # this information in the db, then the last attempt time will
            # become further and further into the past.
            cluster.cluster_update_attempt_time = now
            try:
                cluster.save()
            except Exception:
                error = traceback.format_exc()
                self.stdout.flush()
                self.stderr.write(error)
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
