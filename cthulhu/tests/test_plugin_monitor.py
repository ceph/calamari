from cthulhu.manager import plugin_monitor
from django.utils.unittest import TestCase


class TestPluginMonitor(TestCase):
    def setUp(self):
        self.plugin_monitor = plugin_monitor.PluginMonitor(None)

    def tearDown(self):
        pass

    def testCreatePluginMonitor(self):
        pass


class TestPluginLoading(TestCase):

    def setUp(self):
        self.plugin_monitor = plugin_monitor.PluginMonitor(None)

    @skipIf(os.environ.get('CALAMARI_CONFIG') is None, "needs CALAMARI_CONFIG set")
    def testImportStatusProcessor(self):
        plugins = self.plugin_monitor.load_plugins()[0]
        assert(plugins[0] == 'acmeplugin')
        assert(plugins[1].period == 1)

    @skipIf(os.environ.get('CALAMARI_CONFIG') is None, "needs CALAMARI_CONFIG set")
    def testImportError(self):
        # TODO this is a little cryptic since I don't feel like patching the config object right now
        plugins = self.plugin_monitor.load_plugins()
        assert(len(plugins) == 1)  # wilyplugin should bomb

