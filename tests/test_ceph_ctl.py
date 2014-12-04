from django.utils.unittest import TestCase
from ceph_ctl import ExternalCephControl


class TestableExternalCephControl(ExternalCephControl):
    def __init__(self):
        # Override the __init__ in the base-class to avoid config parsing
        self.default_pools = set(['foo', 'bar'])


class TestExternalCephControl(TestCase):
    def setUp(self):
        self.ext_ceph_ctl = TestableExternalCephControl()

    def test_osd_stat_down_and_out(self):
        osds = {"osds": [
            {"osd": 0, "up": 0, "in": 0},
            {"osd": 1, "up": 1, "in": 1}]}
        self.assertEquals(self.ext_ceph_ctl._check_osds_in_and_up(osds), False)

    def test_osd_stat_up_not_in(self):
        osds = {"osds": [
            {"osd": 0, "up": 1, "in": 0},
            {"osd": 1, "up": 1, "in": 1}]}

        self.assertEqual(self.ext_ceph_ctl._check_osds_in_and_up(osds), False)

    def test_osd_stat_in_not_up(self):
        osds = {"osds": [
            {"osd": 0, "up": 0, "in": 1},
            {"osd": 1, "up": 1, "in": 1}]}
        self.assertEqual(self.ext_ceph_ctl._check_osds_in_and_up(osds), False)

    def test_osd_stat_up_and_in(self):
        osds = {"osds": [
            {"osd": 0, "up": 1, "in": 1},
            {"osd": 1, "up": 1, "in": 1}]}
        self.assertEqual(self.ext_ceph_ctl._check_osds_in_and_up(osds), True)

    def test_default_pools_only(self):
        pools = set(['foo', 'bar'])
        self.assertTrue(self.ext_ceph_ctl._check_default_pools_only(pools))

    def test_default_pools_only_too_few(self):
        pools = set(['foo'])
        self.assertFalse(self.ext_ceph_ctl._check_default_pools_only(pools))

    def test_default_pools_only_too_many(self):
        pools = set(['foo', 'bar', 'baz'])
        self.assertFalse(self.ext_ceph_ctl._check_default_pools_only(pools))

    def test_pg_stat_less_active_and_clean(self):
        self.assertFalse(self.ext_ceph_ctl._check_pgs_active_and_clean(
            'v233: 192 pgs: 1 active+clean; 0 bytes data, 34836 KB used, 926 GB / 926 GB avail'))

    def test_pg_stat_active_and_clean(self):
        self.assertTrue(self.ext_ceph_ctl._check_pgs_active_and_clean(
            'v228: 192 pgs: 192 active+clean; 0 bytes data, 108 MB used, 2778 GB / 2778 GB avail'))

    def test_pg_stat_active_remapped(self):
        self.assertFalse(self.ext_ceph_ctl._check_pgs_active_and_clean(
            'v238: 192 pgs: 192 active+remapped; 0 bytes data, 76072 KB used, 1852 GB / 1852 GB avail'))
