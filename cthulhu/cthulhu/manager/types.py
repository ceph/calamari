
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
        else:
            self.osds_by_id = {}
            self.pools_by_id = {}


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
