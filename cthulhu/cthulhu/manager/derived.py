from collections import defaultdict

from calamari_common.types import OsdMap, PgSummary, MdsMap, MonStatus, ServiceId


PG_FIELDS = ['pgid', 'acting', 'up', 'state']
OSD_FIELDS = ['uuid', 'up', 'in', 'up_from', 'public_addr',
              'cluster_addr', 'heartbeat_back_addr', 'heartbeat_front_addr']


CRIT_STATES = set(['stale', 'down', 'peering', 'inconsistent', 'incomplete'])
WARN_STATES = set(['creating', 'recovery_wait', 'recovering', 'replay',
                   'splitting', 'degraded', 'remapped', 'scrubbing', 'repair',
                   'wait_backfill', 'backfilling', 'backfill_toofull'])
OKAY_STATES = set(['active', 'clean'])


class DerivedObjects(dict):
    """
    Store for items which we generate as a function of sync objects, decorated
    versions etc.
    """

    def __init__(self):
        super(DerivedObjects, self).__init__()

    def get(self, key, default=None):
        return super(DerivedObjects, self).get(key, default)

    def set(self, key, value):
        self[key] = value


class OsdPgDetail(object):
    depends = [OsdMap, PgSummary]
    provides = ['osds', 'osds_by_pg_state']

    @classmethod
    def generate(cls, cluster_monitor, server_monitor, data):
        osd_map = cluster_monitor.get_sync_object(OsdMap)

        pg_summary = data[PgSummary]
        # map osd id to pg states
        pg_states_by_osd = defaultdict(lambda: defaultdict(lambda: 0))
        # map osd id to set of pools
        pools_by_osd = defaultdict(lambda: set([]))
        # map pg state to osd ids
        osds_by_pg_state = defaultdict(lambda: set([]))

        # get the list of pools
        pools_by_id = dict((p_id, p['pool_name']) for (p_id, p) in osd_map.pools_by_id.items())

        for pool_id, osds in osd_map.osds_by_pool.items():
            for osd_id in osds:
                pools_by_osd[osd_id].add(pools_by_id[pool_id])

        for osd_id, osd_pg_summary in pg_summary['by_osd'].items():
            for state_tuple, count in osd_pg_summary.items():
                for state in state_tuple.split("+"):
                    osds_by_pg_state[state].add(osd_id)
                    pg_states_by_osd[osd_id][state] += count

        # convert set() to list to make JSON happy
        osds_by_pg_state = dict((k, list(v)) for k, v in
                                osds_by_pg_state.iteritems())

        # helper to modify each osd object
        def fixup_osd(osd):
            osd_id = osd['osd']
            data = dict((k, osd[k]) for k in OSD_FIELDS)
            data.update({'id': osd_id})
            data.update({'osd': osd_id})
            data.update({'pg_states': dict(pg_states_by_osd[osd_id])})
            data.update({'pools': list(pools_by_osd[osd_id])})

            server = server_monitor.get_by_service(ServiceId(
                cluster_monitor.fsid, 'osd', str(osd_id)
            ))

            data.update({'host': server.hostname if server else None})
            data.update({'fqdn': server.fqdn if server else None})
            return data

        # add the pg states to each osd
        osds = map(fixup_osd, osd_map.osds_by_id.values())

        return {
            'osds': osds,
            'osds_by_pg_state': osds_by_pg_state
        }


class HealthCounters(object):
    depends = [OsdMap, MdsMap, MonStatus, PgSummary]
    provides = ['counters']

    @classmethod
    def generate(cls, cluster_monitor, server_monitor, data):
        return {'counters': {
            'osd': cls._calculate_osd_counters(data[OsdMap]),
            'mds': cls._calculate_mds_counters(data[MdsMap]),
            'mon': cls._calculate_mon_counters(data[MonStatus]),
            'pg': cls._calculate_pg_counters(data[PgSummary]),
        }}

    @classmethod
    def _calculate_mon_counters(cls, mon_status):
        mons = mon_status['monmap']['mons']
        quorum = mon_status['quorum']
        ok, warn, crit = 0, 0, 0
        for mon in mons:
            rank = mon['rank']
            if rank in quorum:
                ok += 1
            # TODO: use 'have we had a salt heartbeat recently' here instead
            # elif self.try_mon_connect(mon):
            #    warn += 1
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

    @classmethod
    def _pg_counter_helper(cls, states, classifier, count, stats):
        matched_states = classifier.intersection(states)
        if len(matched_states) > 0:
            stats[0] += count
            for state in matched_states:
                stats[1][state] += count
            return True
        return False

    @classmethod
    def _calculate_pg_counters(cls, pg_summary):
        # Although the mon already has a copy of this (in 'status' output),
        # it's such a simple thing to recalculate here and simplifies our
        # sync protocol.

        pgs_by_state = pg_summary['all']
        ok, warn, crit = [[0, defaultdict(int)] for _ in range(3)]
        for state_name, count in pgs_by_state.items():
            states = map(lambda s: s.lower(), state_name.split("+"))
            if cls._pg_counter_helper(states, CRIT_STATES, count, crit):
                pass
            elif cls._pg_counter_helper(states, WARN_STATES, count, warn):
                pass
            elif cls._pg_counter_helper(states, OKAY_STATES, count, ok):
                pass
        return {
            'ok': {
                'count': ok[0],
                'states': dict(ok[1]),
            },
            'warn': {
                'count': warn[0],
                'states': dict(warn[1]),
            },
            'critical': {
                'count': crit[0],
                'states': dict(crit[1]),
            },
        }

    @classmethod
    def _calculate_osd_counters(cls, osd_map):
        osds = osd_map['osds']
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

    @classmethod
    def _calculate_mds_counters(cls, mds_map):
        up = len(mds_map['up'])
        inn = len(mds_map['in'])
        total = len(mds_map['info'])
        return {
            'total': total,
            'up_in': inn,
            'up_not_in': up - inn,
            'not_up_not_in': total - up,
        }


generators = [OsdPgDetail, HealthCounters]
