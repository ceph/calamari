from cthulhu.util import memoize


class SyncObject(object):
    """
    An object from a Ceph cluster that we are maintaining
    a copy of on the Calamari server.

    We wrap these JSON-serializable objects in a python object to:

    - Decorate them with things like id-to-entry dicts
    - Have a generic way of seeing the version of an object

    """
    def __init__(self, version, data):
        self.version = version
        self.data = data

    @classmethod
    def cmp(cls, a, b):
        """
        Slight bastardization of cmp.  Takes two versions,
        and returns a cmp-like value, except that if versions
        are not sortable we only return 0 or 1.
        """
        # Version is something unique per version (like a hash)
        return 1 if a != b else 0


class VersionedSyncObject(SyncObject):
    @classmethod
    def cmp(cls, a, b):
        # Version is something numeric like an epoch
        return cmp(a, b)


class OsdMap(VersionedSyncObject):
    str = 'osd_map'

    def __init__(self, version, data):
        super(OsdMap, self).__init__(version, data)
        if data is not None:
            self.osds_by_id = dict([(o['osd'], o) for o in data['osds']])
            self.pools_by_id = dict([(p['pool'], p) for p in data['pools']])
            self.osd_tree_node_by_id = dict([(o['id'], o) for o in data['tree']['nodes'] if o['id'] >= 0])
        else:
            self.osds_by_id = {}
            self.pools_by_id = {}
            self.osd_tree_node_by_id = {}

    @memoize
    def get_tree_nodes_by_id(self):
        return dict((n["id"], n) for n in self.data['tree']["nodes"])

    @memoize
    def get_pool_crush_root_nodes(self, pool_id):
        """
        Get the nearest-root nodes in the crush map which enclose the OSDs which
        may be used in this pool.
        """
        pool = self.pools_by_id[pool_id]
        # Select the rules that apply to this pool, via ruleset
        crush_rules = [rule for rule in self.data['crush']['rules'] if rule['ruleset'] == pool['crush_ruleset']]

        root_node_ids = set()
        for rule in crush_rules:
            for step in rule['steps']:
                if step['op'] == "take":
                    root_node_ids.add(step['item'])

        return root_node_ids

    @property
    @memoize
    def pool_osds(self):
        """
        Get the OSDS which may be used in this pool

        :return dict of pool ID to OSD IDs in the pool
        """

        nodes_by_id = self.get_tree_nodes_by_id()

        def _gather_leaves(node):
            result = set()
            for child_id in node['children']:
                if child_id >= 0:
                    result.add(child_id)
                else:
                    result |= _gather_leaves(nodes_by_id[child_id])

            return result

        result = {}
        for pool_id in self.pools_by_id.keys():
            osd_ids = set()
            for node_id in self.get_pool_crush_root_nodes(pool_id):
                osd_ids |= _gather_leaves(nodes_by_id[node_id])
            result[pool_id] = list(osd_ids)

        return result

    @property
    @memoize
    def osd_pools(self):
        """
        A dict of OSD ID to list of pool IDs
        """
        osds = dict([(osd_id, []) for osd_id in self.osds_by_id.keys()])
        for pool_id in self.pools_by_id.keys():
            for in_pool_id in self.pool_osds[pool_id]:
                osds[in_pool_id].append(pool_id)

        return osds


class MdsMap(VersionedSyncObject):
    str = 'mds_map'


class MonMap(VersionedSyncObject):
    str = 'mon_map'


class MonStatus(VersionedSyncObject):
    str = 'mon_status'

    def __init__(self, version, data):
        super(MonStatus, self).__init__(version, data)
        if data is not None:
            self.mons_by_rank = dict([(m['rank'], m) for m in data['monmap']['mons']])
        else:
            self.mons_by_rank = {}


class PgBrief(SyncObject):
    str = 'pg_brief'


class Health(SyncObject):
    str = 'health'


OSD = 'osd'
POOL = 'pool'
CRUSH_RULE = 'crush_rule'
CLUSTER = 'cluster'

# The objects that ClusterMonitor keeps copies of from the mon
SYNC_OBJECT_TYPES = [MdsMap, OsdMap, MonMap, MonStatus, PgBrief, Health]
SYNC_OBJECT_STR_TYPE = dict((t.str, t) for t in SYNC_OBJECT_TYPES)
