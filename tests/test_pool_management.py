
import logging
from nose.exc import SkipTest
from tests.server_testcase import RequestTestCase

log = logging.getLogger(__name__)


# Long enough for PGs to be created AND for a cluster heartbeat to happen to complete the request
# PG creation is highly cluster dependent, this is a "finger in the air"
PG_REQUEST_PERIOD = 600


class TestPoolManagement(RequestTestCase):
    def setUp(self):
        super(TestPoolManagement, self).setUp()
        self.ceph_ctl.configure(3)
        self.calamari_ctl.configure()

    def _filter_pool(self, pools, pool_name):
        for pool in pools:
            if pool['name'] == pool_name:
                return pool
        return None

    def _create(self, cluster_id, pool_name, pg_num=64, optionals=None):
        # Check that the pool we're going to create doesn't already exist
        self.assertEqual(self._filter_pool(self.api.get("cluster/%s/pool" % cluster_id).json(), pool_name), None)

        # Create the pool
        args = {
            'name': pool_name,
            'pg_num': pg_num
        }
        if optionals:
            args.update(optionals)

        # TODO fix this default value
        if 'hashpspool' in args:
            args['hashpspool'] = int(args['hashpspool'])

        log.debug("TPM._create {argh}".format(argh=str(args)))
        r = self.api.post("cluster/%s/pool" % cluster_id, args)
        self._wait_for_completion(r)

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
        if 'pg_num' in attrs:
            timeout = PG_REQUEST_PERIOD
        else:
            timeout = None
        r = self.api.patch("cluster/%s/pool/%s" % (cluster_id, pool_id), attrs)
        self._wait_for_completion(r, timeout=timeout)

    def _delete(self, cluster_id, pool_id):
        # Delete the pool
        r = self.api.delete("cluster/%s/pool/%s" % (cluster_id, pool_id))
        self._wait_for_completion(r)

    def test_lifecycle(self):
        """
        Test that we can:
         - Create a pool
         - Add some PGs to it
         - Delete it
        """

        cluster_id = self._wait_for_cluster()

        pool_name = 'test1'

        self._create(cluster_id, pool_name, pg_num=64)
        pool_id = self._assert_visible(cluster_id, pool_name)['id']

        # TODO: check on the cluster that it's really present (with the correct parameters), not just
        # on the calamari server

        self._update(cluster_id, pool_id, {'pg_num': 128})
        self._assert_attribute(cluster_id, pool_id, pg_num=128)

        self._delete(cluster_id, pool_id)
        self._assert_visible(cluster_id, pool_name, visible=False)

        # TODO: check on the cluster that it's really gone, not just on calamari server

    def _get_version(self):
        self._wait_for_servers()

        fqdns = self.ceph_ctl.get_server_fqdns()

        # Pick any server, assume tests aren't mixed version
        version = self.api.get("server/{0}".format(fqdns[0])).json()['ceph_version']
        log.debug("version = %s" % version)

        return version.split(".")

    def _get_min_size(self, config):
        min_size = int(config['osd_pool_default_min_size'])
        default_size = int(config['osd_pool_default_size'])
        if min_size:
            min_size = min(min_size, default_size)
        else:
            min_size = default_size - int(default_size / 2.)

        return min_size

    def _non_default_args(self, fsid):
        """
        Get some pool arguments that are different to the defaults.  Because the
        defaults depend on the Ceph version, this is conditional on that too.
        """

        args = {
            'size': 4,
            'crash_replay_interval': 120,
            'crush_ruleset': 1,
            'quota_max_objects': 42,
            'quota_max_bytes': 42000000
        }

        crush_rules = self.api.get("cluster/{0}/crush_rule".format(fsid)).json()
        if len(crush_rules) <= 1:
            del(args['crush_ruleset'])

        config = self.api.get("cluster/{0}/config".format(fsid)).json()
        config = dict([(i['key'], i['value']) for i in config])

        args['min_size'] = self._get_min_size(config) + 1

        if self._get_version() > (0, 67, 7):
            log.debug("Including hashpspool in non_default_args")
            default_hashpspool = config['osd_pool_default_flag_hashpspool'] == 'true'
            args['hashpspool'] = False if default_hashpspool else True
        else:
            log.debug("Old ceph: excluding hashpspool from non_default_args")

        return args

    def _min_size_testvals(self, size):
        '''
        return a list of tuples of (test values, expected result) for
        changing min_size relative to the argument 'size'
        '''
        return [
            (size, size),
            (size + 1, size),
            (size - 1, size - 1),
            (0, size - size / 2)
        ]

    def test_create_args(self):
        """
        Test that when non-default attributes are passed to create, they are
        accepted and reflected on the created pool.
        """

        cluster_id = self._wait_for_cluster()

        # Some non-default values
        optionals = self._non_default_args(cluster_id)
        for minsize, minsize_exp in self._min_size_testvals(optionals['size']):
            pool_name = 'test1'
            optionals['min_size'] = minsize
            self._create(cluster_id, pool_name, pg_num=64, optionals=optionals)
            pool_id = self._assert_visible(cluster_id, pool_name)['id']
            pool = self.api.get("cluster/%s/pool/%s" %
                                (cluster_id, pool_id)).json()
            for var, val in optionals.items():
                # for min_size, the value set may be modified;
                # use 'expected' rather than exact 'val'
                if var == 'min_size':
                    val = minsize_exp
                self.assertEqual(pool[var], val,
                                 "pool[%s]!=%s (actually %s)" %
                                 (var, val, pool[var]))
                # TODO: call out to the ceph cluster to check the
                # value landed
            # remove pool to try next minsize value
            self._delete(cluster_id, pool_id)

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
        mods = self._non_default_args(cluster_id)
        for var, val in mods.items():
            if var == 'min_size':
                continue  # need to set size first. this will fail if it is not in range of 1-size
            # Sanity check we really are changing something, that the new val is diff
            self.assertNotEqual(pool[var], val, '%s did not change' % (var))
            try:
                self._update(cluster_id, pool_id, {var: val})
                pool = self.api.get("cluster/%s/pool/%s" % (cluster_id, pool_id)).json()
                self.assertEqual(pool[var], val)
                # TODO: call out to the ceph cluster to check the
                # value landed
            except:
                log.exception("Exception updating %s:%s" % (var, val))
                raise

        # test some min_size updates, relative to pool size established
        # above (which we reread here to isolate parts of the test)
        size = self.api.get(
            "cluster/%s/pool/%s" % (cluster_id, pool_id)).json()['size']
        for val, expected in self._min_size_testvals(size):
            try:
                self._update(cluster_id, pool_id, {'min_size': val})
                pool = self.api.get("cluster/%s/pool/%s" % (cluster_id, pool_id)).json()
                self.assertEqual(
                    pool['min_size'], expected,
                    msg="set min_size {0}, expected {1}, got {2}".
                    format(val, expected, pool['min_size'])
                )
                # TODO: call out to the ceph cluster to check the
                # value landed
            except:
                log.exception("Exception updating min_size:%s" % val)
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

    def test_pg_creation(self):
        """
        Test that when modifying the 'pg_num' attribute, the PGs really are
        created and pgp_num is updated appropriately.  This is a separate
        test to the simple modifications, because updating pgp_num is more
        complicated (calamari has to wait for PG creation to occur)
        """
        cluster_id = self._wait_for_cluster()
        pool_name = 'test_pg_creation'
        self._create(cluster_id, pool_name, pg_num=64)
        pool_id = self._assert_visible(cluster_id, pool_name)['id']

        updates = {
            'pg_num': 96,
            'pgp_num': 96
        }
        self._update(cluster_id, pool_id, updates)
        pool = self.api.get("cluster/%s/pool/%s" % (cluster_id, pool_id)).json()
        for k, v in updates.items():
            self.assertEqual(pool[k], v, "pool[%s]=%s (should be %s)" % (k, pool[k], v))

    def test_big_pg_creation(self):
        """
        Test that when creating a number of PGs that exceeds mon_osd_max_split_count
        calamari is breaking up the operation so that it succeeds.
        """

        cluster_id = self._wait_for_cluster()
        pool_name = 'test_big_pg_creation'
        self._create(cluster_id, pool_name, pg_num=64)
        pool_id = self._assert_visible(cluster_id, pool_name)['id']

        config_response = self.api.get("cluster/%s/config/mon_osd_max_split_count" % cluster_id)
        if config_response.status_code == 404:
            raise SkipTest("Pre-firefly Ceph, skipping mon_osd_max_split_count test")
        else:
            config_response.raise_for_status()

        mon_osd_max_split_count = int(config_response.json()['value'])
        pool = self.api.get("cluster/%s/pool/%s" % (cluster_id, pool_id)).json()
        osd_count = len(self.api.get("cluster/%s/osd" % cluster_id).json())
        pgs_to_create = osd_count * mon_osd_max_split_count * 2
        new_pg_num = pool['pg_num'] + pgs_to_create

        self._update(cluster_id, pool_id, {'pg_num': new_pg_num})
        pool = self.api.get("cluster/%s/pool/%s" % (cluster_id, pool_id)).json()
        self.assertEqual(pool['pg_num'], new_pg_num)
        self.assertEqual(pool['pgp_num'], new_pg_num)
