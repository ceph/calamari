from django.utils.unittest import TestCase
from django.utils.unittest.case import skipIf
import os
from mock import Mock

if os.environ.get('CALAMARI_CONFIG'):
    from cthulhu.manager import plugin_monitor


class StatusProcessor(object):

    @property
    def period(self):
        return 1

    def run(self, check_data):

        state = "OK"
        if not check_data:
            state = "FAIL"
        for node, data in check_data.iteritems():
            for key, value in data.iteritems():
                if key == 'SMART Health Status' and value != "OK":
                    state = "FAIL"

        return {'SMART Health Status': state}


class TestStatusChecksIntegration(TestCase):

    def setUp(self):
        # FIXME depends on magic defined in minion-sim
        fqdn_mocks = [Mock(fqdn='figment00%s.imagination.com' % str(x)) for x in range(3)]
        servers_mock = Mock(get_all=Mock())
        servers_mock.get_all.return_value = fqdn_mocks
        self.plugin_monitor = plugin_monitor.PluginMonitor(servers_mock)

    def kill_plugin(self, check_data):
        self.plugin_monitor.stop()
        status_processor = StatusProcessor()
        return status_processor.run(check_data)

    @skipIf(True, "depends on minion-sim running")
    def testRunPlugin(self):
        self.plugin_monitor.run_plugin('wilyplugin', self.kill_plugin, 1)

        assert(self.plugin_monitor.plugin_results['wilyplugin'] == {"SMART Health Status": "OK"})
