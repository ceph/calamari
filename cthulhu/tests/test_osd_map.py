from django.utils.unittest.case import TestCase
from unittest.case import TestCase as UnitTestCase
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

    def test_7883(self):
        """
        Bug in which pools were not found for OSDs
        """
        osd_map = OsdMap(None, load_fixture("osd_map-7883.json"))
        all_osds = osd_map.osds_by_id.keys()
        self.assertEqual(len(all_osds), 168)

        self.assertDictEqual(osd_map.osds_by_rule_id, {
            0: all_osds,
            1: all_osds,
            2: all_osds
        })

        self.assertDictEqual(osd_map.osds_by_pool, {
            0: all_osds,
            1: all_osds,
            2: all_osds
        })


class TestCrushNodes(UnitTestCase):

    def test_parent_map_none(self):
        osd_map = OsdMap(None, None)
        assert None == osd_map._map_parent_buckets({})

    def test_parent_map_one(self):
        tree_nodes = [
            {"children": [],
             "type": "rack",
             "id": -5,
             "name": "83988b9c-4a63-11e4-8c64-000c29066317",
             "type_id": 2,
             },
            {"children": [-5],
             "type": "root",
             "id": -1,
             "name": "default",
             "type_id": 6,
             }
        ]

        osd_map = OsdMap(None, None)
        assert osd_map._map_parent_buckets(tree_nodes) == {
            -5: {"children": [-5],
                 "type": "root",
                 "id": -1,
                 "name": "default",
                 "type_id": 6
                 }
        }

    def test_parent_map_some(self):
        tree_nodes = [
            {"children": [-4, -3, -2],
             "type": "root",
             "id": -1,
             "name": "default",
             "type_id": 6
             }
        ]

        osd_map = OsdMap(None, None)
        assert osd_map._map_parent_buckets(tree_nodes) == {
            -4: {"children": [-4, -3, -2],
                 "type": "root",
                 "id": -1,
                 "name": "default",
                 "type_id": 6
                 },
            -3: {"children": [-4, -3, -2],
                 "type": "root",
                 "id": -1,
                 "name": "default",
                 "type_id": 6
                 },
            -2: {"children": [-4, -3, -2],
                 "type": "root",
                 "id": -1,
                 "name": "default",
                 "type_id": 6
                 },
        }

    def test_parent_map_many(self):
        tree_nodes = [
            {
                "children": [],
                "type": "rack",
                "id": -5,
                "name": "83988b9c-4a63-11e4-8c64-000c29066317",
                "type_id": 2
            },
            {
                "children": [
                    -4,
                    -2,
                    -3
                ],
                "type": "root",
                "id": -1,
                "name": "default",
                "type_id": 6
            },
            {
                "children": [
                    1
                ],
                "type": "host",
                "id": -3,
                "name": "vpm068",
                "type_id": 1
            },
            {
                "status": "up",
                "name": "osd.1",
                "exists": 1,
                "reweight": "1.000000",
                "type_id": 0,
                "crush_weight": "0.399994",
                "depth": 2,
                "type": "osd",
                "id": 1
            },
            {
                "children": [
                    0
                ],
                "type": "host",
                "id": -2,
                "name": "vpm114",
                "type_id": 1
            },
            {
                "status": "up",
                "name": "osd.0",
                "exists": 1,
                "reweight": "1.000000",
                "type_id": 0,
                "crush_weight": "0.099991",
                "depth": 2,
                "type": "osd",
                "id": 0
            },
            {
                "children": [
                    2
                ],
                "type": "host",
                "id": -4,
                "name": "vpm140",
                "type_id": 1
            },
            {
                "status": "up",
                "name": "osd.2",
                "exists": 1,
                "reweight": "1.000000",
                "type_id": 0,
                "crush_weight": "0.099991",
                "depth": 2,
                "type": "osd",
                "id": 2
            }
        ]

        osd_map = OsdMap(None, None)
        assert osd_map._map_parent_buckets(tree_nodes) == {-4: {'children': [-4, -2, -3],
                                                                'id': -1,
                                                                'name': 'default',
                                                                'type': 'root',
                                                                'type_id': 6},
                                                           -3: {'children': [-4, -2, -3],
                                                                'id': -1,
                                                                'name': 'default',
                                                                'type': 'root',
                                                                'type_id': 6},
                                                           -2: {'children': [-4, -2, -3],
                                                                'id': -1,
                                                                'name': 'default',
                                                                'type': 'root',
                                                                'type_id': 6},
                                                           0: {'children': [0],
                                                               'id': -2,
                                                               'name': 'vpm114',
                                                               'type': 'host',
                                                               'type_id': 1},
                                                           1: {'children': [1],
                                                               'id': -3,
                                                               'name': 'vpm068',
                                                               'type': 'host',
                                                               'type_id': 1},
                                                           2: {'children': [2],
                                                               'id': -4,
                                                               'name': 'vpm140',
                                                               'type': 'host',
                                                               'type_id': 1}}
