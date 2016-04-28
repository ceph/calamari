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
