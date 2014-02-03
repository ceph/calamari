from django.utils.unittest import TestCase
import os

from cthulhu.manager import plugin_monitor, config

config.set('cthulhu', 'plugin_path', os.path.abspath(os.path.join(os.path.dirname(__file__), "plugins/")))


class TestPluginLoading(TestCase):
    def setUp(self):
        self.plugin_monitor = plugin_monitor.PluginMonitor(None)

    def testImportStatusProcessor(self):
        plugins = self.plugin_monitor.load_plugins()[0]
        assert (plugins[0] == 'acmeplugin')
        assert (plugins[1].period == 1)

    def testImportError(self):
        # TODO this is a little cryptic since I don't feel like patching the config object right now
        plugins = self.plugin_monitor.load_plugins()
        assert (len(plugins) == 1)  # wilyplugin should bomb
