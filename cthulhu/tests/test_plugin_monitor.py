from cthulhu.manager import plugin_monitor
from unittest import TestCase
from mock import MagicMock, patch
from datetime import datetime, timedelta


class TestPluginMonitor(TestCase):
    def setUp(self):
        self.plugin_monitor = plugin_monitor.PluginMonitor()

    def tearDown(self):
        pass

    def testCreatePluginMonitor(self):
        pass

    def testRunCheckTakesCorrectTime(self):
        period = 5
        # self.plugin_monitor.salt_client = MagicMock()
        now = datetime.now()
        self.plugin_monitor.run_check('foo', period)
        later = datetime.now()
        assert(timedelta(seconds=period + 1) > later - now > timedelta(seconds=period))

        