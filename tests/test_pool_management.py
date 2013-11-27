
from tests.server_testcase import ServerTestCase, HEARTBEAT_INTERVAL
from tests.utils import wait_until_true


# TODO: This would be lower/more aggressive if we didn't have to wait
# for a full upgrade cycle for OSD maps to update (should be updating
# them more aggressively as part of the UserRequest)
operation_timeout = HEARTBEAT_INTERVAL


class TestPoolManagement(ServerTestCase):
    def _request_complete(self, cluster_id, request_id):
        r = self.api.get("cluster/%s/request/%s" % (cluster_id, request_id))
        r.raise_for_status()

        return r.json()['state'] == 'complete'

    def setUp(self):
        super(TestPoolManagement, self).setUp()
        self.ceph_ctl.configure(3)
        self.calamari_ctl.configure()

    def _filter_pool(self, pools, pool_name):
        for pool in pools:
            if pool['name'] == pool_name:
                return pool
        return None

    def _create(self, cluster_id, pool_name, pg_num=64, optionals={}):
        # Check that the pool we're going to create doesn't already exist
        self.assertEqual(self._filter_pool(self.api.get("cluster/%s/pool" % cluster_id).json(), pool_name), None)

        # Create the pool
        args = {
            'name': pool_name,
            'pg_num': pg_num
        }
        args.update(optionals)
        r = self.api.post("cluster/%s/pool" % cluster_id, args)
        r.raise_for_status()
        request_id = r.json()['request_id']
        wait_until_true(lambda: self._request_complete(cluster_id, request_id), timeout=operation_timeout)

    def _assert_visible(self, cluster_id, pool_name, visible=True):
        # Check the pool is now visible
        r = self.api.get("cluster/%s/pool" % cluster_id)
        r.raise_for_status()
        pool = self._filter_pool(r.json(), pool_name)
        if visible:
            self.assertNotEqual(pool, None)
            return pool
        else:
            self.assertEqual(pool, None)

    def _assert_attribute(self, cluster_id, pool_id, **kwargs):
        pool = self.api.get("cluster/%s/pool/%s" % (cluster_id, pool_id)).json()
        for k, v in kwargs.items():
            self.assertEqual(pool[k], v)

    def _update(self, cluster_id, pool_id, attrs):
        r = self.api.patch("cluster/%s/pool/%s" % (cluster_id, pool_id), attrs)
        r.raise_for_status()
        request_id = r.json()['request_id']
        wait_until_true(lambda: self._request_complete(cluster_id, request_id), timeout=operation_timeout)
        return self.api.get("cluster/%s/request/%s" % (cluster_id, request_id)).json()

    def _delete(self, cluster_id, pool_id):
        # Delete the pool
        r = self.api.delete("cluster/%s/pool/%s" % (cluster_id, pool_id))
        r.raise_for_status()
        request_id = r.json()['request_id']
        wait_until_true(lambda: self._request_complete(cluster_id, request_id), timeout=operation_timeout)

    def test_lifecycle(self):
        """
        Test that we can:
         - Create a pool
         - Add some PGs to it
         - Delete it
        """

        cluster_id = self._wait_for_cluster()

        pool_name = 'test1'

        # TODO: in creation, support setting crush ruleset
        self._create(cluster_id, pool_name, pg_num=64)
        pool_id = self._assert_visible(cluster_id, pool_name)['id']

        # TODO: check on the cluster that it's really present (with the correct parameters), not just
        # on the calamari server

        self._update(cluster_id, pool_id, {'pg_num': 128})
        self._assert_attribute(cluster_id, pool_id, pg_num=128)

        self._delete(cluster_id, pool_id)
        self._assert_visible(cluster_id, pool_name, visible=False)

        # TODO: check on the cluster that it's really gone, not just on calamari server

    def test_create_args(self):
        """
        Test that when non-default attributes are passed to create, they are
        accepted and reflected on the created pool.
        """

        # Some non-default values
        optionals = {
            'size': 3,
            'min_size': 2,
            'crash_replay_interval': 120,
            'crush_ruleset': 1,
            'hashpspool': True,
            'quota_max_objects': 42,
            'quota_max_bytes': 42000000
        }

        cluster_id = self._wait_for_cluster()
        pool_name = 'test1'
        self._create(cluster_id, pool_name, pg_num=64, optionals=optionals)
        pool_id = self._assert_visible(cluster_id, pool_name)['id']
        pool = self.api.get("cluster/%s/pool/%s" % (cluster_id, pool_id)).json()
        for var, val in optionals.items():
            self.assertEqual(pool[var], val, "pool[%s]!=%s (actually %s)" % (
                var, val, pool[var]
            ))

    def test_modification(self):
        """
        Check that valid modifications to a pool are accepted and actioned.
        """

        cluster_id = self._wait_for_cluster()
        pool_name = 'test1'
        self._create(cluster_id, pool_name, pg_num=64)
        pool_id = self._assert_visible(cluster_id, pool_name)['id']
        pool = self.api.get("cluster/%s/pool/%s" % (cluster_id, pool_id)).json()

        # Some non-default values
        mods = {
            'size': 3,
            'min_size': 2,
            'crash_replay_interval': 120,
            'pg_num': 256,
            # NB skipping pgp_num because setting pg_num will
            # set it automatically
            #'pgp_num': 256,
            'crush_ruleset': 1,
            'hashpspool': True,
            'quota_max_objects': 42,
            'quota_max_bytes': 42000000
        }
        for var, val in mods.items():
            # Sanity check we really are changing something, that the new val is diff
            self.assertNotEqual(pool[var], val)
            try:
                self._update(cluster_id, pool_id, {var: val})
                pool = self.api.get("cluster/%s/pool/%s" % (cluster_id, pool_id)).json()
                self.assertEqual(pool[var], val)
                # TODO: call out to the ceph cluster to check the
                # value landed
            except:
                print "Exception updating %s:%s" % (var, val)
                raise

    def test_rename(self):
        """
        What it sounds like:

        - can we rename a pool?
        - what happens if the name is bad?
        - what happens if the name collides with another pool?
        """
        cluster_id = self._wait_for_cluster()
        pool_name = 'test1'
        self._create(cluster_id, pool_name, pg_num=64)
        pool_id = self._assert_visible(cluster_id, pool_name)['id']

        new_name = 'test1_changed'
        self._update(cluster_id, pool_id, {'name': new_name})
        self._assert_visible(cluster_id, pool_name, visible=False)
        self._assert_visible(cluster_id, new_name)

    def test_coherency(self):
        """
        Test that once a job modifying a cluster map is complete, subsequent reads
        of the cluster map immediately reflect the change (i.e.  test that cluster map
        modifying jobs are not marked as complete until their change is readable).

        This test is timing-sensitive in a way that favors passes.  This is unavoidably racy
        (because our read is always some finite time after the job completion).  This is a
        'real life' test, for a deterministic test of the order of events, look to unit testing.
        """

        cluster_id = self._wait_for_cluster()

        pool_name = 'testcoherent'
        attempts = 10
        for i in range(attempts):
            self._create(cluster_id, pool_name)
            pool_id = self._assert_visible(cluster_id, pool_name)['id']
            self._delete(cluster_id, pool_id)
            self._assert_visible(cluster_id, pool_name, visible=False)

    # TODO: document the creation semantics for REST API consumers: that on creation
    # and pg_num increase, we promise the OSD map will be up to date when the job completes,
    # but we make no assurances about the resulting PG creations: to learn when they complete
    # REST API consumer would have to watch the PG state.
