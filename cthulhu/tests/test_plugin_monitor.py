from cthulhu.manager import plugin_monitor
from nose.tools import with_setup
import sys
import types
from unittest import TestCase


class status_check(TestCase):

    frequency = .75
    @staticmethod
    def run():
        pass

class status_processor_fail(TestCase):
    def __init__(self):
        raise ImportError

class fakeProcessor(TestCase):

    @staticmethod
    def run():
        return {'name': 'acmeplugin', 'values': 12345}

class TestPluginMonitor(TestCase):
    def setUp(self):
        self.plugin_monitor = plugin_monitor.PluginMonitor(plugin_path='cthulhu/cthulhu/tests/plugins')

    def tearDown(self):
        pass

    def testCreatePluginMonitor(self):
        pass


    # This is an integration test since we are loading files
    # TODO move it elsewhere
    # TODO figure out what todo about PYTHONPATH
    def testImportStatusProcessor(self):
        plugins = self.plugin_monitor.load_plugins()
        assert(isinstance(plugins[0][0], types.ModuleType))


class TestStatusChecksIntegration(TestCase):

    def setUp(self):
        self.plugin_monitor = plugin_monitor.PluginMonitor(plugin_path='cthulhu/cthulhu/tests/plugins')


    def tearDown(self):
        pass

    # TODO I am an integration test that requires minion-sim ATM
     # also remember that I am some-what non-deterministic depending on the tolerance of timeout
    def testRunChecks(self):
        out = self.plugin_monitor.run_check(status_check)
        assert(out.values()[0] == {'ret': '{"SMART Health Status": "OK"}'}) 

    # TODO this isn't really a valid test since we aren't checking that we can instanciate
    def testLoadingStatusCheck(self):
        plugins = self.plugin_monitor.load_plugins()
        assert(isinstance(plugins[0][0], types.ModuleType))

    def testThatFakeAndFileEquate(self):
        pass

class TestModules(TestCase):
    def setUp(self):
        self.plugin_monitor = plugin_monitor.PluginMonitor(plugin_path='cthulhu/cthulhu/tests/plugins')

    def tearDown(self):
        pass

    def testLoadingCheckFailingProcessor(self):
        self.plugin_monitor.load_plugins()

    def testBlowingNose(self):
        # assert(False)
        pass