import logging

from unittest import TestCase
from calamari_rest.views.crush_node import lookup_ancestry

log = logging.getLogger(__name__)


class TestCrushNodeAncestry(TestCase):

    def setUp(self):
        pass

    def testNone(self):
        osd_id = 0
        fake_parent_map = {}
        self.assertEqual([], lookup_ancestry(osd_id, fake_parent_map))

    def testOne(self):
        osd_id = 0
        fake_parent_map = {0: [{'id': -1}]}
        self.assertEqual([[-1]], lookup_ancestry(osd_id, fake_parent_map))

    def testSome(self):
        osd_id = 0
        fake_parent_map = dict([(x, [{'id': x + 1}]) for x in range(-5, -1)])
        fake_parent_map[osd_id] = [{'id': -5}]
        self.assertEqual([[-5, -4, -3, -2, -1]], lookup_ancestry(osd_id, fake_parent_map))

    def test_many(self):
        osd_id = 0
        # This is unrealistic no CRUSH tree should ever be this deep
        depth = -50000
        fake_parent_map = dict([(x, [{'id': x + 1}]) for x in range(depth, -1)])
        fake_parent_map[osd_id] = [{'id': depth}]
        self.assertEqual([range(depth, 0)], lookup_ancestry(osd_id, fake_parent_map))

    def test_some_multiple_osd_mapping(self):
        osd_id = 0
        fake_parent_map = {0: [{'id': -1}, {'id': -2}], -1: [{'id': -3}], -2: [{'id': -3}]}
        self.assertEqual([[-1, -3], [-2, -3]], lookup_ancestry(osd_id, fake_parent_map))

    def test_strange_map(self):
        osd_id = 1
        fake_parent_map = {-5: [{'id': -10, }],
                           -4: [{'id': -5, },
                                {'id': -1}],
                           -3: [{'id': -5, },
                                {'id': -1}],
                           -2: [{'id': -5, },
                                {'id': -1}],
                           1: [{'id': -20, },
                               {'id': -2}]}

        self.assertEqual([[-20], [-2, -5, -10]], lookup_ancestry(osd_id, fake_parent_map))
