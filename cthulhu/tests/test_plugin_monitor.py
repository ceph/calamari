from cthulhu.manager import plugin_monitor
from unittest import TestCase


class TestPluginMonitor(TestCase):
    def setUp(self):
        self.plugin_monitor = plugin_monitor.PluginMonitor()

    def tearDown(self):
        pass

    def testCreatePluginMonitor(self):
        pass
