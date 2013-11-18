from collections import defaultdict
import datetime
from django.conf import settings
import os
from pytz import utc

settings.configure(
    DATABASES={'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ['CALAMARI_DB']
    }},
    USE_TZ=True
)

from ceph.models import Cluster


PG_FIELDS = ['pgid', 'acting', 'up', 'state']
OSD_FIELDS = ['uuid', 'up', 'in', 'up_from', 'public_addr',
              'cluster_addr', 'heartbeat_back_addr', 'heartbeat_front_addr']

CRIT_STATES = set(['stale', 'down', 'peering', 'inconsistent', 'incomplete'])
WARN_STATES = set(['creating', 'recovery_wait', 'recovering', 'replay',
                   'splitting', 'degraded', 'remapped', 'scrubbing', 'repair',
                   'wait_backfill', 'backfilling', 'backfill_toofull'])
OKAY_STATES = set(['active', 'clean'])


def get_or_create(cluster_name, cluster_fsid):
    # Note that this is a sleazy "only ever one cluster" implementation
    try:
        cluster = Cluster.objects.get()
    except Cluster.DoesNotExist:
        cluster = Cluster.objects.create(name=cluster_name, id=cluster_fsid)
    else:
        if cluster.name != cluster_name or cluster.id != cluster_fsid:
            cluster.delete()
            cluster = Cluster.objects.create(name=cluster_name, id=cluster_fsid)

    return cluster


def heartbeat():
    cluster = Cluster.objects.get()
    cluster.cluster_update_time = datetime.datetime.utcnow().replace(tzinfo=utc)
    cluster.save()


def populate_health(health_detail):
    cluster = Cluster.objects.get()

    cluster.health = {
        'overall_status': health_detail['overall_status'],
        'detail': health_detail['detail'],
        'summary': health_detail['summary'],
    }
    cluster.save()


def populate_counters(osd_map, mds_map, mon_status, pg_brief_map):
    cluster = Cluster.objects.get()

    cluster.counters = {
        'osd': _calculate_osd_counters(osd_map),
        'mds': _calculate_mds_counters(mds_map),
        'mon': _calculate_mon_counters(mon_status),
        'pg': _calculate_pg_counters(pg_brief_map),
    }

    cluster.save()


def populate_osds_and_pgs(osd_map, osd_tree, pgs):
    """Fill in the PG and OSD lists

    :param pgs: Brief PG map
    :param osd_tree: OSD tree from CRUSH map (osdtree format)
    :param osd_map: OSD map
    """

    cluster = Cluster.objects.get()

    # map osd id to pg states
    pg_states_by_osd = defaultdict(lambda: defaultdict(lambda: 0))
    # map osd id to set of pools
    pools_by_osd = defaultdict(lambda: set([]))
    # map pg state to osd ids
    osds_by_pg_state = defaultdict(lambda: set([]))

    # helper to modify each pg object
    def fixup_pg(pg):
        data = dict((k, pg[k]) for k in PG_FIELDS)
        data['state'] = data['state'].split("+")
        return data

    # save the brief pg map
    cluster.pgs = map(fixup_pg, pgs)

    # get the list of pools
    pools_by_id = dict((d['pool'], d['pool_name']) for d in osd_map['pools'])

    # populate the indexes
    for pg in cluster.pgs:
        pool_id = int(pg['pgid'].split(".")[0])
        acting = set(pg['acting'])
        for state in pg['state']:
            osds_by_pg_state[state] |= acting
            for osd_id in acting:
                pg_states_by_osd[osd_id][state] += 1
                if pool_id in pools_by_id:
                    pools_by_osd[osd_id] |= set([pools_by_id[pool_id]])

    # convert set() to list to make JSON happy
    osds_by_pg_state = dict((k, list(v)) for k, v in
                            osds_by_pg_state.iteritems())
    cluster.osds_by_pg_state = osds_by_pg_state

    # get the osd tree. we'll use it to get hostnames
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
        data = dict((k, osd[k]) for k in OSD_FIELDS)
        data.update({'id': osd_id})
        data.update({'pg_states': pg_states_by_osd[osd_id]})
        data.update({'pools': list(pools_by_osd[osd_id])})
        data.update({'host': host_by_osd_name["osd.%d" % (osd_id,)]})
        return data

    # add the pg states to each osd
    cluster.osds = map(fixup_osd, osd_map['osds'])

    cluster.save()
