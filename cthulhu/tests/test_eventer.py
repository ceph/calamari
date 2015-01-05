from django.utils.unittest import TestCase
from cthulhu.manager.eventer import Eventer
from django.utils.unittest.case import skipIf
import os
from mock import MagicMock


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
