from django.utils.unittest import TestCase
from ceph_ctl import ExternalCephControl


class TestableExternalCephControl(ExternalCephControl):
    def __init__(self):
        # Override the __init__ in the base-class to avoid config parsing
        pass


class TestExternalCephControl(TestCase):
    def setUp(self):
        self.ext_ceph_ctl = TestableExternalCephControl()

    def test_osd_stat_down_and_out(self):
        stat_output = '''
        {"osds": [
        { "osd": 0,
          "uuid": "6a42162d-2dd8-4984-b7fe-2cc372cec028",
          "up": 0,
          "in": 0,
          "state": [
                "exists",
                "up"]},
        { "osd": 1,
          "uuid": "d5b9047c-d1af-4488-82cb-1e681d20fe06",
          "up": 1,
          "in": 1,
          "state": [
                "exists",
                "up"]}
        ]}
        '''
        self.assertEquals(self.ext_ceph_ctl._get_osds_down_or_out(stat_output), {'down': [0], 'out': [0]})

    def test_osd_stat_up_not_in(self):
        stat_output = '''
        {"osds": [
        { "osd": 0,
          "uuid": "6a42162d-2dd8-4984-b7fe-2cc372cec028",
          "up": 1,
          "in": 0,
          "state": [
                "exists",
                "up"]},
        { "osd": 1,
          "uuid": "d5b9047c-d1af-4488-82cb-1e681d20fe06",
          "up": 1,
          "in": 1,
          "state": [
                "exists",
                "up"]}
        ]}
        '''
        self.assertEqual(self.ext_ceph_ctl._get_osds_down_or_out(stat_output), {'down': [], 'out': [0]})

    def test_osd_stat_in_not_up(self):
        stat_output = '''
        {"osds": [
        { "osd": 0,
          "uuid": "6a42162d-2dd8-4984-b7fe-2cc372cec028",
          "up": 0,
          "in": 1,
          "state": [
                "exists",
                "up"]},
        { "osd": 1,
          "uuid": "d5b9047c-d1af-4488-82cb-1e681d20fe06",
          "up": 1,
          "in": 1,
          "state": [
                "exists",
                "up"]}
        ]}
        '''
        self.assertEqual(self.ext_ceph_ctl._get_osds_down_or_out(stat_output), {'down': [0], 'out': []})

    def test_osd_stat_up_and_in(self):
        stat_output = '''
        {"osds": [
        { "osd": 0,
          "uuid": "6a42162d-2dd8-4984-b7fe-2cc372cec028",
          "up": 1,
          "in": 1,
          "state": [
                "exists",
                "up"]},
        { "osd": 1,
          "uuid": "d5b9047c-d1af-4488-82cb-1e681d20fe06",
          "up": 1,
          "in": 1,
          "state": [
                "exists",
                "up"]}
        ]}
        '''
        self.assertEqual(self.ext_ceph_ctl._get_osds_down_or_out(stat_output), {'down': [], 'out': []})

    def test_default_pools_only(self):
        lspools_output = '\n[\n    { "poolnum": 0,\n      "poolname": "data"},\n    { "poolnum": 1,\n      "poolname": "metadata"},\n    { "poolnum": 2,\n      "poolname": "rbd"}]\n'
        self.assertTrue(self.ext_ceph_ctl._check_default_pools_only(lspools_output))

    def test_default_pools_only_missing_data(self):
        lspools_output = '\n[\n    { "poolnum": 0,\n      "poolname": "not_data"},\n    { "poolnum": 1,\n      "poolname": "metadata"},\n    { "poolnum": 2,\n      "poolname": "rbd"}]\n'
        self.assertFalse(self.ext_ceph_ctl._check_default_pools_only(lspools_output))

    def test_default_pools_only_too_few(self):
        lspools_output = '\n[\n   { "poolnum": 1,\n      "poolname": "metadata"},\n    { "poolnum": 2,\n      "poolname": "rbd"}]\n'
        self.assertFalse(self.ext_ceph_ctl._check_default_pools_only(lspools_output))

    def test_default_pools_only_different_ids(self):
        lspools_output = '\n[\n    { "poolnum": 1,\n      "poolname": "data"},\n    { "poolnum": 0,\n      "poolname": "metadata"},\n    { "poolnum": 2,\n      "poolname": "rbd"}]\n'
        self.assertTrue(self.ext_ceph_ctl._check_default_pools_only(lspools_output))

    def test_pg_stat_less_active_and_clean(self):
        self.assertFalse(self.ext_ceph_ctl._check_pgs_active_and_clean(
            'v233: 192 pgs: 1 active+clean; 0 bytes data, 34836 KB used, 926 GB / 926 GB avail'))

    def test_pg_stat_active_and_clean(self):
        self.assertTrue(self.ext_ceph_ctl._check_pgs_active_and_clean(
            'v228: 192 pgs: 192 active+clean; 0 bytes data, 108 MB used, 2778 GB / 2778 GB avail'))

    def test_pg_stat_active_remapped(self):
        self.assertFalse(self.ext_ceph_ctl._check_pgs_active_and_clean(
            'v238: 192 pgs: 192 active+remapped; 0 bytes data, 76072 KB used, 1852 GB / 1852 GB avail'))
