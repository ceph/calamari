from cthulhu.manager import plugin_monitor
from nose.tools import with_setup
import sys
import types

class status_check(object):

    frequency = .75

    @staticmethod
    def run():
        pass

class status_processor_fail(object):
    def __init__(self):
        raise ImportError

class fakeProcessor(object):

    @staticmethod
    def run():
        return {'name': 'acmeplugin', 'values': 12345}

class TestPluginMonitor(object):
    def setUp(self):
        self.plugin_monitor = plugin_monitor.PluginMonitor(plugin_path='cthulhu/cthulhu/tests/plugins')

    def tearDown(self):
        pass

    def testCreatePluginMonitor(self):
        pass

    def testGettingDataFromOnePlugin(self):
        self.plugin_monitor.status_processors['acmeplugin'] = fakeProcessor
        # sys.stderr.write(str(self.plugin_monitor.status_processors))
        self.plugin_monitor.run_plugins()
        acme_results = self.plugin_monitor.get_data(plugin_name='acmeplugin')
        # sys.stderr.write('whee')
        assert(acme_results == {'name': 'acmeplugin', 'values': 12345})

    def testDataFromTwoPlugins(self):
        self.plugin_monitor.status_processors['acmeplugin'] = fakeProcessor
        # sys.stderr.write(str(self.plugin_monitor.status_processors))
        self.plugin_monitor.run_plugins()
        acme_results = self.plugin_monitor.get_data(plugin_name='acmeplugin')
        assert(acme_results == {'name': 'acmeplugin', 'values': 12345})
        
        # WILY is an ImportError
        # wily_results = self.plugin_monitor.get_data('wilyplugin')
        # assert(wily_results == {'name': 'wilyplugin'})

    # This is an integration test since we are loading files
    # TODO move it elsewhere
    # TODO figure out what todo about PYTHONPATH
    def testImportStatusProcessor(self):
        self.plugin_monitor.load_plugins()
        assert(isinstance(self.plugin_monitor.status_processors.get('acmeplugin'), types.ModuleType))


class TestStatusChecksIntegration(object):

    def setUp(self):
        self.plugin_monitor = plugin_monitor.PluginMonitor(plugin_path='cthulhu/cthulhu/tests/plugins')
        self.plugin_monitor.status_checks['wilyplugin'] = status_check
        self.plugin_monitor.run_status_checks('wilyplugin')

    def tearDown(self):
        pass

    # TODO I am an integration test that requires minion-sim ATM
     # also remember that I am some-what non-deterministic depending on the tolerance of timeout
    def testRunChecks(self):
        out = self.plugin_monitor.plugin_data.get('wilyplugin')
        assert(out.values()[0] == {'ret': '{"SMART Health Status": "OK"}'}) 

    def testRunDataReset(self):
        out_len1 = self.plugin_monitor.plugin_data.get('wilyplugin')
        self.plugin_monitor.run_status_checks('wilyplugin')
        out_len2 = self.plugin_monitor.plugin_data.get('wilyplugin')
        assert(out_len1 == out_len2)

    # TODO this isn't really a valid test since we aren't checking that we can instanciate
    def testLoadingStatusCheck(self):
        self.plugin_monitor.load_plugins()
        assert(isinstance(self.plugin_monitor.status_checks.get('acmeplugin'), types.ModuleType))

    def testThatFakeAndFileEquate(self):
        self.plugin_monitor.load_plugins()
        acmeplugin = self.plugin_monitor.status_checks.get('acmeplugin')
        check = acmeplugin.StatusCheck()
        fake_check = status_check()
        assert(isinstance(acmeplugin, types.ModuleType))
        assert(check.frequency == 5000)
        # assert(check == fake_check)

class TestModules(object):
    def setUp(self):
        self.plugin_monitor = plugin_monitor.PluginMonitor(plugin_path='cthulhu/cthulhu/tests/plugins')

    def tearDown(self):
        pass

    def testLoadingCheckFailingProcessor(self):
        self.plugin_monitor.load_plugins()

    def testBlowingNose(self):
        # assert(False)
        pass