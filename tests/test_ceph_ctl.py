from django.utils.unittest import TestCase
from ceph_ctl import ExternalCephControl

class TestExternalCephControl(TestCase):

    def setUp(self):
        self.ext_ceph_ctl = ExternalCephControl()

    def test_osd_stat_down_and_out(self):
        stat_output = '\n{ "epoch": 14,\n  "num_osds": 3,\n  "num_up_osds": 1,\n  "num_in_osds": "1",\n  "full": "false",\n  "nearfull": "false"}'
        self.assertFalse(self.ext_ceph_ctl._check_osd_up_and_in(stat_output))

    def test_osd_stat_empty_response(self):
        self.assertFalse(self.ext_ceph_ctl._check_osd_up_and_in(''))

    def test_osd_stat_bad_json(self):
        stat_output = '\n "epoch": 14,\n  "num_osds": 3,\n  "num_up_osds": 1,\n  "num_in_osds": "1",\n  "full": "false",\n  "nearfull": "false"}'
        self.assertFalse(self.ext_ceph_ctl._check_osd_up_and_in(stat_output))

    def test_osd_stat_up_not_in(self):
        stat_output = '\n{ "epoch": 14,\n  "num_osds": 3,\n  "num_up_osds": 3,\n  "num_in_osds": "1",\n  "full": "false",\n  "nearfull": "false"}'
        self.assertFalse(self.ext_ceph_ctl._check_osd_up_and_in(stat_output))

    def test_osd_stat_in_not_up(self):
        stat_output = '\n{ "epoch": 14,\n  "num_osds": 3,\n  "num_up_osds": 1,\n  "num_in_osds": "3",\n  "full": "false",\n  "nearfull": "false"}'
        self.assertFalse(self.ext_ceph_ctl._check_osd_up_and_in(stat_output))

    def test_osd_stat_up_and_in(self):
        stat_output = '\n{ "epoch": 14,\n  "num_osds": 3,\n  "num_up_osds": 3,\n  "num_in_osds": "3",\n  "full": "false",\n  "nearfull": "false"}'
        self.assertTrue(self.ext_ceph_ctl._check_osd_up_and_in(stat_output))

    def test_default_pools_only(self):
        lspools_output = '\n[\n    { "poolnum": 0,\n      "poolname": "data"},\n    { "poolnum": 1,\n      "poolname": "metadata"},\n    { "poolnum": 2,\n      "poolname": "rbd"}]\n'
        self.assertTrue(self.ext_ceph_ctl._check_default_pools_only(lspools_output))

    def test_default_pools_only_empty_output(self):
        self.assertFalse(self.ext_ceph_ctl._check_default_pools_only(''))

    def test_default_pools_only_missing_data(self):
        lspools_output = '\n[\n    { "poolnum": 0,\n      "poolname": "not_data"},\n    { "poolnum": 1,\n      "poolname": "metadata"},\n    { "poolnum": 2,\n      "poolname": "rbd"}]\n'
        self.assertFalse(self.ext_ceph_ctl._check_default_pools_only(lspools_output))

    def test_default_pools_only_too_few(self):
        lspools_output = '\n[\n   { "poolnum": 1,\n      "poolname": "metadata"},\n    { "poolnum": 2,\n      "poolname": "rbd"}]\n'
        self.assertFalse(self.ext_ceph_ctl._check_default_pools_only(lspools_output))

    def test_default_pools_only_bad_json(self):
        lspools_output = '\n[\n     "poolnum": 0,\n      "poolname": "data"},\n    { "poolnum": 1,\n      "poolname": "metadata"},\n    { "poolnum": 2,\n      "poolname": "rbd"}]\n'
        self.assertFalse(self.ext_ceph_ctl._check_default_pools_only(lspools_output))

    def test_default_pools_only_different_ids(self):
        lspools_output = '\n[\n    { "poolnum": 1,\n      "poolname": "data"},\n    { "poolnum": 0,\n      "poolname": "metadata"},\n    { "poolnum": 2,\n      "poolname": "rbd"}]\n'
        self.assertTrue(self.ext_ceph_ctl._check_default_pools_only(lspools_output))

    def test_pg_stat_less_active_and_clean(self):
        self.assertFalse(self.ext_ceph_ctl._check_pgs_active_and_clean('v233: 192 pgs: 1 active+clean; 0 bytes data, 34836 KB used, 926 GB / 926 GB avail'))

    def test_pg_stat_empty(self):
        self.assertFalse(self.ext_ceph_ctl._check_pgs_active_and_clean(''))

    def test_pg_stat_active_and_clean(self):
        self.assertTrue(self.ext_ceph_ctl._check_pgs_active_and_clean('v228: 192 pgs: 192 active+clean; 0 bytes data, 108 MB used, 2778 GB / 2778 GB avail'))

    def test_pg_stat_active_remapped(self):
        self.assertFalse(self.ext_ceph_ctl._check_pgs_active_and_clean('v238: 192 pgs: 192 active+remapped; 0 bytes data, 76072 KB used, 1852 GB / 1852 GB avail'))
