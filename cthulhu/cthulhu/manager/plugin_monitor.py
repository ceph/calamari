import gevent
from gevent import Timeout
import importlib
import os
import salt.client
import sys
from cthulhu.manager import config
from cthulhu.log import log

class PluginMonitor(gevent.greenlet.Greenlet):
    """
    Consumes output from plugins
    """

    def __init__(self):
        super(PluginMonitor, self).__init__()
        self.salt_client = salt.client.LocalClient(config.get('cthulhu', 'salt_config_path'))

    def load_plugins(self):
        ret_val = []
        """
        Try to load a status_processor from each module in plugin_path, store keyed by module_name
        """
        for plugin in os.listdir(config.get('cthulhu', 'plugin_path')):
            plugin = plugin.split('.')[0]
            if plugin in ('__init__', 'README'):
                continue
            # sys.stderr.write(plugin)
            status_processor = None
            try:
                status_processor = importlib.import_module('.'.join((plugin, 'status_processor')))
                # TODO make an instance
            except ImportError:
                log.exception("Error importing plugin %s" % plugin)

            ret_val.append(status_processor)

            return ret_val

    def run_plugin(self, plugin_name, status_processor, period):
        while(1):
            check_data = self.run_check(plugin_name, period)
            log.debug("processed " +str(plugin_name) + str(check_data))
            return status_processor(check_data)

    def run_check(self, plugin_name, period):
        ret_val = {}
        timeout = Timeout(period)

        salt_name = '.'.join((plugin_name,'status_check'))
        ret = self.salt_client.cmd_iter_no_block('*', salt_name)

        timeout.start()
        finished = False
        try:
            for value in ret:
                # TODO this is ugly hideous scraping, there must be a better way to tell that Salt doesn't have a particular status_check
                if value.values()[0] == {'ret': '"%s" is not available.' % salt_name}:
                    log.error("Plugin %s is not available on %s" % (salt_name, value.keys()[0]))
                    continue

                ret_val.update(value)

            finished = True
            gevent.sleep(period)
        except Timeout, t:
            if t is not timeout:
                raise # someone else getting timed out

            if not finished:
                log.exception("Did not finish %s" % salt_name)

        return ret_val
        # TODO run the status processor