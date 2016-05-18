from unittest.case import TestCase as UnitTestCase
from tests.util import load_fixture

from cthulhu.manager.crush_rule_request_factory import _merge_rule_and_map, _serialize_rule


# An OSD map with some non-default CRUSH rules in it
INTERESTING_OSD_MAP = load_fixture('interesting_osd_map.json')

REPLICATED_RULE = {"id": 0,
                   "name": "racky",
                   "ruleset": 1,
                   "type": "replicated",
                   "min_size": 1,
                   "max_size": 10,
                   "steps": [
                       {
                           "item_name": "default",
                           "item": -1,
                           "op": "take"
                       },
                       {
                           "num": 0,
                           "type": "rack",
                           "op": "chooseleaf_firstn"
                       },
                       {
                           "op": "emit"
                       }
                   ],
                   "osd_count": 0
                   }

ERASURE_RULE = {"id": 2,
                "name": "ecruleset",
                "ruleset": 2,
                "type": "erasure",
                "min_size": 3,
                "max_size": 3,
                "steps": [
                    {
                        "num": 5,
                        "op": "set_chooseleaf_tries"
                    },
                    {
                        "num": 100,
                        "op": "set_choose_tries"
                    },
                    {
                        "item_name": "default",
                        "item": -1,
                        "op": "take"
                    },
                    {
                        "num": 0,
                        "type": "host",
                        "op": "chooseleaf_indep"
                    },
                    {
                        "op": "emit"
                    }
                ],
                "osd_count": 0
                }

REPLICATED_RULE_UPDATE = {"id": 0,
                          "name": "racky_updated",
                          "ruleset": 1,
                          "type": "replicated",
                          "min_size": 2,
                          "max_size": 11,
                          "steps": [
                              {
                                  "item_name": "default",
                                  "item": -1,
                                  "op": "take"
                              },
                              {
                                  "num": 0,
                                  "type": "row",
                                  "op": "chooseleaf_firstn"
                              },
                              {
                                  "op": "emit"
                              }
                          ],
                          "osd_count": 0
                          }

ERASURE_RULE_UPDATE = {"id": 2,
                       "name": "ecrule_updated",
                       "ruleset": 2,
                       "type": "erasure",
                       "min_size": 3,
                       "max_size": 3,
                       "steps": [
                           {
                               "num": 6,
                               "op": "set_chooseleaf_tries"
                           },
                           {
                               "num": 101,
                               "op": "set_choose_tries"
                           },
                           {
                               "item_name": "default",
                               "item": -1,
                               "op": "take"
                           },
                           {
                               "num": 0,
                               "type": "rack",
                               "op": "chooseleaf_indep"
                           },
                           {
                               "op": "emit"
                           }
                       ],
                       "osd_count": 0
                       }


with open('replicated_rule_crush_repr.txt') as f:
    REPLICATED_RULE_CRUSH_REPR = f.read()

with open('erasure_rule_crush_repr.txt') as f:
    ERASURE_RULE_CRUSH_REPR = f.read()

with open('crush_map_repr_before.txt') as f:
    CRUSH_REPR_BEFORE_CREATE = f.read()

with open('crush_map_repr_after.txt') as f:
    CRUSH_REPR_AFTER_CREATE = f.read()

with open('crush_map_repr_before_update.txt') as f:
    CRUSH_REPR_BEFORE_UPDATE = f.read()

with open('crush_map_repr_after_update.txt') as f:
    CRUSH_REPR_AFTER_UPDATE = f.read()


class TestCrushRule(UnitTestCase):

    def test_serialize_rule_replicated(self):
        """
        That the correct OSDs are recognised as part of a CRUSH rule
        """
        self.assertEqual(_serialize_rule(REPLICATED_RULE, 1), REPLICATED_RULE_CRUSH_REPR)

    def test_serialize_rule_erasure(self):
        """
        That the correct OSDs are recognised as part of a CRUSH rule
        """
        self.assertEqual(_serialize_rule(ERASURE_RULE, 2), ERASURE_RULE_CRUSH_REPR)

    def test_merge_rule_and_map_create(self):
        merged = _merge_rule_and_map(CRUSH_REPR_BEFORE_CREATE, ERASURE_RULE)
        assert merged == CRUSH_REPR_AFTER_CREATE

    def test_merge_rule_and_map_update(self):
        merged = _merge_rule_and_map(CRUSH_REPR_BEFORE_UPDATE, REPLICATED_RULE_UPDATE, 'racky')
        merged = _merge_rule_and_map(merged, ERASURE_RULE_UPDATE, 'ecruleset')
        assert merged == CRUSH_REPR_AFTER_UPDATE
