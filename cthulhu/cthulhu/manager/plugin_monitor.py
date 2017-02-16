import gevent
from gevent import event
import importlib
import os
import time

from cthulhu.manager import config
from cthulhu.log import log


class PluginMonitor(gevent.greenlet.Greenlet):
    """
    Consumes output from plugins for a specific cluster
    """

    def __init__(self, servers):
        super(PluginMonitor, self).__init__()
        # plugin_name to status processor output
        self.plugin_results = {}
        self._complete = event.Event()
        self._servers = servers

    def load_plugins(self):

        """
        Try to load a status_processor from each module in plugin_path, store keyed by module_name
        """
        loaded_plugins = []
        # FIXME this assumes that plugin_path has been added to PYTHONPATH and/or is in site-packages
        plugin_path = config.get('cthulhu', 'plugin_path')

        if os.path.exists(plugin_path):
            for plugin in os.listdir(plugin_path):
                plugin = plugin.split('.')[0]
                if plugin in ('__init__', 'README'):
                    continue

                status_processor = None
                try:
                    plugin_module = importlib.import_module('.'.join((plugin, 'status_processor')))
                    status_processor = plugin_module.StatusProcessor()
                except ImportError, e:
                    log.info("Error importing plugin %s %s" % (plugin, str(e)))

                if status_processor is not None:
                    loaded_plugins.append((plugin, status_processor))

        return loaded_plugins

    def filter_errors(self, check_data, salt_name):
        filtered_output = {}
        for node, results in check_data.iteritems():
            if results == '"%s" is not available.' % salt_name:
                log.info(node + results)
            else:
                filtered_output[node] = results

        return filtered_output

    def run_plugin(self, plugin_name, status_processor, period):
        # slice of some time for the checks, leaving some for the status_processor
        check_timeout = int(period * .75)
        salt_name = '.'.join((plugin_name, 'status_check'))

        while not self._complete.is_set():
            start = int(time.time())
            timeout_at = start + period
            servers = [s.fqdn for s in self._servers.get_all()]
            check_data = self.filter_errors(self._remote_run_cmd_async(servers,
                                                                       salt_name,
                                                                       timeout=check_timeout),
                                            salt_name)

            self.plugin_results[plugin_name] = status_processor(check_data)
            log.debug("processed " + str(plugin_name) + str(check_data))

            time_left = timeout_at - int(time.time())
            gevent.sleep(max(0, time_left))

    def _run(self):
        log.info("Starting %s" % self.__class__.__name__)
        threads = [gevent.spawn(self.run_plugin,
                                name,
                                status_processor.run,
                                status_processor.period) for name, status_processor in self.load_plugins()]

        gevent.joinall(threads)

    def stop(self):
        self._complete.set()
