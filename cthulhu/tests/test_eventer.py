from django.utils.unittest import TestCase
from cthulhu.manager.eventer import Eventer
from django.utils.unittest.case import skipIf
import os
from mock import MagicMock, patch


class TestEventer(TestCase):
    def setUp(self):
        self.eventer = Eventer(MagicMock())

    def tearDown(self):
        pass

    @skipIf(os.environ.get('CALAMARI_CONFIG') is None, "needs CALAMARI_CONFIG set")
    def testCreateManager(self):
        assert self.eventer is not None

    def test_that_it_emits_deleted_osd_events(self):
        self.eventer._emit = MagicMock()
        new = MagicMock()
        old = MagicMock()
        old.data = {}
        old.data['osds'] = [{'osd': 0}]
        self.eventer._on_osd_map(12345, new, old)
        self.assertIn('removed from the cluster map', '\n'.join([str(x) for x in self.eventer._emit.call_args_list]))

    def test_that_it_emits_added_osd_events(self):
        self.eventer._emit = MagicMock()
        new = MagicMock()
        old = MagicMock()
        new.data = {}
        new.data['osds'] = [{'osd': 0}]
        self.eventer._on_osd_map(12345, new, old)
        self.assertIn('added to the cluster map', '\n'.join([str(x) for x in self.eventer._emit.call_args_list]))

    @patch('cthulhu.manager.eventer.salt.client')
    def test_that_it_emits_quorum_status_events(self, client):
        new = MagicMock()
        old = MagicMock()
        old.data = {
            "election_epoch": 2,
            "monmap": {
                "created": "0.000000",
                "epoch": 1,
                "fsid": "fc0dc0f5-fe35-48c1-8c9c-f2ae0770fce7",
                "modified": "0.000000",
                "mons": [
                    {
                        "addr": "198.199.75.124:6789/0",
                        "name": "vagrant-ubuntu-trusty-64",
                        "rank": 0
                    }
                ]
            },
            "quorum": [
                0
            ],
            "quorum_leader_name": "",
            "quorum_names": [
                "vagrant-ubuntu-trusty-64"
            ]
        }

        new.data = {
            "election_epoch": 2,
            "monmap": {
                "created": "0.000000",
                "epoch": 1,
                "fsid": "fc0dc0f5-fe35-48c1-8c9c-f2ae0770fce7",
                "modified": "0.000000",
                "mons": [
                    {
                        "addr": "198.199.75.124:6789/0",
                        "name": "vagrant-ubuntu-trusty-64",
                        "rank": 0
                    }
                ]
            },
            "quorum": [
                0
            ],
            "quorum_leader_name": "vagrant-ubuntu-trusty-64",
            "quorum_names": [
                "vagrant-ubuntu-trusty-64"
            ]
        }

        self.eventer._emit = MagicMock()
        self.eventer._on_quorum_status(12345, new, new)
        self.assertFalse(self.eventer._emit.called)

        self.eventer._on_quorum_status(12345, new, old)
        message = '\n'.join([str(x) for x in self.eventer._emit.call_args_list])
        print message
        self.assertIn('now quorum leader', message)

    def test_that_it_emits_pool_events(self):
        self.eventer._emit = MagicMock()
        new = MagicMock()
        old = MagicMock()
        old.data = {}
        old.data["pools"] = [
            {
                "auid": 0,
                "cache_min_evict_age": 0,
                "cache_min_flush_age": 0,
                "cache_mode": "none",
                "cache_target_dirty_high_ratio_micro": 600000,
                "cache_target_dirty_ratio_micro": 400000,
                "cache_target_full_ratio_micro": 800000,
                "crash_replay_interval": 0,
                "crush_ruleset": 0,
                "erasure_code_profile": "",
                "expected_num_objects": 0,
                "fast_read": False,
                "flags": 1,
                "flags_names": "hashpspool",
                "hit_set_count": 0,
                "hit_set_params": {
                    "type": "none"
                },
                "hit_set_period": 0,
                "last_change": "7",
                "last_force_op_resend": "0",
                "min_read_recency_for_promote": 0,
                "min_size": 1,
                "min_write_recency_for_promote": 0,
                "object_hash": 2,
                "pg_num": 64,
                "pg_placement_num": 64,
                "pool": 1,
                "pool_name": "data",
                "pool_snaps": [],
                "quota_max_bytes": 0,
                "quota_max_objects": 0,
                "read_tier": -1,
                "removed_snaps": "[]",
                "size": 1,
                "snap_epoch": 0,
                "snap_mode": "selfmanaged",
                "snap_seq": 0,
                "stripe_width": 0,
                "target_max_bytes": 0,
                "target_max_objects": 0,
                "tier_of": -1,
                "tiers": [],
                "type": 1,
                "use_gmt_hitset": True,
                "write_tier": -1
            }]

        new.data = {}
        new.data["pools"] = [
            {
                "auid": 0,
                "cache_min_evict_age": 0,
                "cache_min_flush_age": 0,
                "cache_mode": "none",
                "cache_target_dirty_high_ratio_micro": 0,
                "cache_target_dirty_ratio_micro": 0,
                "cache_target_full_ratio_micro": 0,
                "crash_replay_interval": 0,
                "crush_ruleset": 0,
                "erasure_code_profile": "",
                "expected_num_objects": 0,
                "fast_read": False,
                "flags": 1,
                "flags_names": "hashpspool",
                "hit_set_count": 0,
                "hit_set_params": {
                    "type": "none"
                },
                "hit_set_period": 0,
                "last_change": "1",
                "last_force_op_resend": "0",
                "min_read_recency_for_promote": 0,
                "min_size": 1,
                "min_write_recency_for_promote": 0,
                "object_hash": 2,
                "pg_num": 64,
                "pg_placement_num": 64,
                "pool": 0,
                "pool_name": "rbd",
                "pool_snaps": [],
                "quota_max_bytes": 0,
                "quota_max_objects": 0,
                "read_tier": -1,
                "removed_snaps": "[]",
                "size": 1,
                "snap_epoch": 0,
                "snap_mode": "selfmanaged",
                "snap_seq": 0,
                "stripe_width": 0,
                "target_max_bytes": 0,
                "target_max_objects": 0,
                "tier_of": -1,
                "tiers": [],
                "type": 1,
                "use_gmt_hitset": True,
                "write_tier": -1
            },
            {
                "auid": 0,
                "cache_min_evict_age": 0,
                "cache_min_flush_age": 0,
                "cache_mode": "none",
                "cache_target_dirty_high_ratio_micro": 600000,
                "cache_target_dirty_ratio_micro": 400000,
                "cache_target_full_ratio_micro": 800000,
                "crash_replay_interval": 0,
                "crush_ruleset": 0,
                "erasure_code_profile": "",
                "expected_num_objects": 0,
                "fast_read": False,
                "flags": 1,
                "flags_names": "hashpspool",
                "hit_set_count": 0,
                "hit_set_params": {
                    "type": "none"
                },
                "hit_set_period": 0,
                "last_change": "7",
                "last_force_op_resend": "0",
                "min_read_recency_for_promote": 0,
                "min_size": 1,
                "min_write_recency_for_promote": 0,
                "object_hash": 2,
                "pg_num": 64,
                "pg_placement_num": 64,
                "pool": 1,
                "pool_name": "data",
                "pool_snaps": [],
                "quota_max_bytes": 0,
                "quota_max_objects": 0,
                "read_tier": -1,
                "removed_snaps": "[]",
                "size": 1,
                "snap_epoch": 0,
                "snap_mode": "selfmanaged",
                "snap_seq": 0,
                "stripe_width": 0,
                "target_max_bytes": 0,
                "target_max_objects": 0,
                "tier_of": -1,
                "tiers": [],
                "type": 1,
                "use_gmt_hitset": True,
                "write_tier": -1,
            }]

        self.eventer._on_pool_status(12345, old, old)
        self.assertFalse(self.eventer._emit.called)

        self.eventer._on_pool_status(12345, new, old)
        self.assertIn('added to cluster', '\n'.join([str(x) for x in self.eventer._emit.call_args_list]))
        self.eventer._on_pool_status(12345, old, new)
        self.assertIn('removed from cluster', '\n'.join([str(x) for x in self.eventer._emit.call_args_list]))
