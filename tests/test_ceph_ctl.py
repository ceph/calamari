from django.utils.unittest import TestCase
from ceph_ctl import ExternalCephControl

class TestExternalCephControl(TestCase):

    def setUp(self):
        self.ext_ceph_ctl = ExternalCephControl()

    def test_osd_stat_down_and_out(self):
        self.assertFalse(self.ext_ceph_ctl._check_osd_up_and_in('e17: 3 osds: 0 up, 0 in'))

    def test_osd_stat_empty_response(self):
        self.assertFalse(self.ext_ceph_ctl._check_osd_up_and_in(''))

    def test_osd_stat_changed_format(self):
        self.assertFalse(self.ext_ceph_ctl._check_osd_up_and_in('e17: 3 osds: 0 up, 0 in, 0 scrubbing'))

    def test_osd_stat_up_not_in(self):
        self.assertFalse(self.ext_ceph_ctl._check_osd_up_and_in('e17: 3 osds: 3 up, 0 in'))

    def test_osd_stat_in_not_up(self):
        self.assertFalse(self.ext_ceph_ctl._check_osd_up_and_in('e17: 3 osds: 1 up, 3 in'))

    def test_osd_stat_up_and_in(self):
        self.assertTrue(self.ext_ceph_ctl._check_osd_up_and_in('e17: 3 osds: 3 up, 3 in'))

    def test_pg_stat_less_active_and_clean(self):
        self.assertFalse(self.ext_ceph_ctl._check_pgs_active_and_clean('v233: 192 pgs: 1 active+clean; 0 bytes data, 34836 KB used, 926 GB / 926 GB avail'))

    def test_pg_stat_empty(self):
        self.assertFalse(self.ext_ceph_ctl._check_pgs_active_and_clean(''))

    def test_pg_stat_active_and_clean(self):
        self.assertTrue(self.ext_ceph_ctl._check_pgs_active_and_clean('v228: 192 pgs: 192 active+clean; 0 bytes data, 108 MB used, 2778 GB / 2778 GB avail'))

    def test_pg_stat_active_remapped(self):
        self.assertFalse(self.ext_ceph_ctl._check_pgs_active_and_clean('v238: 192 pgs: 192 active+remapped; 0 bytes data, 76072 KB used, 1852 GB / 1852 GB avail'))
