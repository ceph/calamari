from unittest import TestCase
from django.utils.unittest.case import skipIf
import mock
import gevent
import os

if os.environ.get('CALAMARI_CONFIG'):
   from cthulhu.manager import plugin_monitor


class StatusProcessor(object):

    @property
    def period(self):
        return 1

    def run(self, check_data):

        state = "OK"
        for node, data in check_data.iteritems():
            for key, value in data.iteritems():
                if key == 'SMART Health Status' and value != "OK":
                    state = "FAIL"

        return {'SMART Health Status': state}


class TestPluginLoading(TestCase):

    def setUp(self):
        self.plugin_monitor = plugin_monitor.PluginMonitor()

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


class TestStatusChecksIntegration(TestCase):

    def setUp(self):
        self.plugin_monitor = plugin_monitor.PluginMonitor()

    def kill_plugin(self, check_data):
        self.plugin_monitor.stop()
        status_processor = StatusProcessor()
        return status_processor.run(check_data)

    @skipIf(True, "depends on minion-sim running")
    def testRunPlugin(self):
        self.plugin_monitor.run_plugin('wilyplugin', self.kill_plugin, 1)

        assert(self.plugin_monitor.plugin_results['wilyplugin'] == {"SMART Health Status": "OK"})
