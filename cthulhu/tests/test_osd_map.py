from django.utils.unittest.case import TestCase

from calamari_common.types import OsdMap
from tests.util import load_fixture


# An OSD map with some non-default CRUSH rules in it
INTERESTING_OSD_MAP = load_fixture('interesting_osd_map.json')


class TestOsdMap(TestCase):
    """
    Tests for the processing that we do on the OSD map to expose
    higher level views.
    """

    def test_crush_osds(self):
        """
        That the correct OSDs are recognised as part of a CRUSH rule
        """
        osd_map = OsdMap(None, INTERESTING_OSD_MAP)

        all_osds = [0, 1, 2, 3, 4, 5]
        first_osds = [0, 2, 4]
        first_server_osds = [0, 1]

        self.assertEqual(osd_map.osds_by_rule_id, {
            0: all_osds,  # Default rule
            1: all_osds,  # Default rule
            2: all_osds,  # Default rule
            3: first_osds,  # My custom one that takes each server's first drive
            4: first_server_osds  # My custom one that takes the drives from the first server
        })

        # By extension, the same OSDs should be recognised as part of
        # the pools using the crush rule
        self.assertEqual(osd_map.osds_by_pool, {
            2: all_osds,
            4: all_osds,
            5: all_osds,
            6: first_osds,
            7: first_server_osds
        })
