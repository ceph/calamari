from cthulhu.manager import plugin_monitor
from nose.tools import with_setup
import sys
import types

class fakeCheck(object):

    @staticmethod
    def run():
        return '["   8       0 sda 23499 3928 620854 11408 65515 74718 1219272 27052 0 21640 38380", "   8       1 sda1 20423 3890 595954 10896 63109 66133 1131344 20592 0 17880 31408"]'


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
        sys.stderr.write(str(self.plugin_monitor.status_processors))
        self.plugin_monitor.run_plugins()
        acme_results = self.plugin_monitor.get_data(plugin_name='acmeplugin')
        # sys.stderr.write('whee')
        assert(acme_results == {'name': 'acmeplugin', 'values': 12345})

    def testDataFromTwoPlugins(self):
        self.plugin_monitor.status_processors['acmeplugin'] = fakeProcessor
        sys.stderr.write(str(self.plugin_monitor.status_processors))
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
        self.plugin_monitor.load_status_processors()
        assert(isinstance(self.plugin_monitor.status_processors.get('acmeplugin'), types.ModuleType))


    # TODO I am an integration test that requires minion-sim ATM
    def testRunChecks(self):

        self.plugin_monitor.status_checks['acmeplugin'] = fakeCheck
        sys.stderr.write(str(self.plugin_monitor.status_checks))
        self.plugin_monitor.run_status_checks()
        assert(self.plugin_monitor.plugin_data['acmeplugin'] == '["   8       0 sda 23499 3928 620854 11408 65515 74718 1219272 27052 0 21640 38380", "   8       1 sda1 20423 3890 595954 10896 63109 66133 1131344 20592 0 17880 31408"]')

    def testLoadingStatusCheck(self):
        self.plugin_monitor.load_status_check()
        assert(isinstance(self.plugin_monitor.status_checks.get('acmeplugin'), types.ModuleType))