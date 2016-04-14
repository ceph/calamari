from django.test import TestCase
import os
import sys

from cthulhu.manager import plugin_monitor, config

plugin_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "plugins/"))
config.set('cthulhu', 'plugin_path', plugin_path)
sys.path.append(plugin_path)


class TestPluginLoading(TestCase):
    def setUp(self):
        self.plugin_monitor = plugin_monitor.PluginMonitor(None)

    def testImportStatusProcessor(self):
        plugins = self.plugin_monitor.load_plugins()[0]
        self.assertEqual(plugins[0], 'acmeplugin')
        self.assertEqual(plugins[1].period, 1)

    def testImportError(self):
        # TODO this is a little cryptic since I don't feel like patching the config object right now
        plugins = self.plugin_monitor.load_plugins()
        self.assertEqual(len(plugins), 1)  # wilyplugin should bomb
