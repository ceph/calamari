
class RequestFactory(object):
    """
    A class to generate UserRequests with commands (e.g. Ceph RADOS admin
    commands) in response to C[r]UD operations.

    The mapping is sometimes very simple (e.g. delete on a pool is
    just a 'ceph osd pool delete'), and sometimes more complex (e.g.
    pool creation requires a 'pool create' followed by a series of
    'pool set' and/or 'pool set-quota' commands).

    """
    def __init__(self, cluster_monitor):
        # The parent ClusterMonitor, we need a reference to see its
        # cluster maps
        self._cluster_monitor = cluster_monitor

    def delete(self, obj_id):
        raise NotImplementedError()

    def update(self, obj_id, attributes):
        raise NotImplementedError()

    def create(self, attributes):
        raise NotImplementedError()
