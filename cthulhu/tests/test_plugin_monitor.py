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

