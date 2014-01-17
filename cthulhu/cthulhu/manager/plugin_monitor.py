import gevent
from gevent import Timeout
import importlib
import os
import salt.client
import sys
from cthulhu.log import log

class PluginMonitor(gevent.greenlet.Greenlet):
    """
    Consumes output from plugins
    """

    def __init__(self, plugin_path, salt_path='dev/etc/salt/master'):
        super(PluginMonitor, self).__init__()
        self.status_processors = {}
        self.status_checks = {}
        # TODO we probably need a different store for the crap we get from the checks and the stuff output by the processor
        self.plugin_data = {}
        self.plugin_path = plugin_path
        self.salt_client = salt.client.LocalClient(c_path=salt_path)


    def get_data(self, plugin_name):
        return self.plugin_data.get(plugin_name)

    def load_plugins(self):
        """
        Try to load a status_check and status_processor from each module in self.plugin_path, store keyed by module_name
        """
        for plugin in os.listdir(self.plugin_path):
            plugin = plugin.split('.')[0]
            if plugin in ('__init__', 'README'):
                continue
            # sys.stderr.write(plugin)
            status_processor = None
            status_check = None
            try:
                # TODO it should be an error loading the plugin if either module fails to load
                status_check = importlib.import_module('.'.join((plugin, 'status_check')))
                status_processor = importlib.import_module('.'.join((plugin, 'status_processor')))
                # TODO make an instance of each
            except ImportError:
                log.exception("Error importing plugin %s" % plugin)

            self.status_processors[plugin] = status_processor
            self.status_checks[plugin] = status_check
               
    # We run this once we've gotten all the checks of a generation
    # TODO rename to run_status_processors and fix it to operate on a different data struct
    def run_plugins(self):
        # TODO we have gevent use it
        for name,x in self.status_processors.iteritems():
            # TODO what about failure
            self.plugin_data[name] = x.run()

    def run_status_checks(self, plugin_name='acmeplugin'):
        # we need to register them once we parse them
        plugin = self.status_checks.get(plugin_name)
        timeout = Timeout(plugin.frequency)
        self.plugin_data[plugin_name] = {}

        ret = self.salt_client.cmd_iter_no_block('*', '.'.join((plugin_name,plugin.__name__)))

        timeout.start()
        finished = False
        try:
            for value in ret:
                # TODO handle the case where salt is telling up that the plugin is not available
                self.plugin_data[plugin_name].update(value)
                gevent.sleep(0)

            finished = True
            gevent.sleep(plugin.frequency)
        except Timeout, t:
            if t is not timeout:
                raise # someone else getting timed out

            if not finished:
                log.exception("Did not finish %s" % plugin)

        # TODO run the status processor