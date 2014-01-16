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
        self.plugin_path = plugin_path
        self.salt_client = salt.client.LocalClient(c_path=salt_path)

    def load_plugins(self):
        ret_val = []
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
                status_check = importlib.import_module('.'.join((plugin, 'status_check')))
                status_processor = importlib.import_module('.'.join((plugin, 'status_processor')))
                # TODO make an instance of each
            except ImportError:
                log.exception("Error importing plugin %s" % plugin)

            ret_val.append((status_check, status_processor))

            return ret_val


    def run_plugin(self, check):
        while(1):
            run = gevent.spawn(check)
            run.join()
            check_data = run.value
            
            # TODO invoke processor here
            log.debug("processed " +str(check) + str(check_data))

    def run_check(self, check):
        ret_val = {}
        # we need to register them once we parse them
        timeout = Timeout(check.frequency)

        # TODO fix the hard code of plugin_name
        ret = self.salt_client.cmd_iter_no_block('*', '.'.join(('wilyplugin',check.__name__)))

        timeout.start()
        finished = False
        try:
            for value in ret:
                # TODO handle the case where salt is telling up that the plugin is not available
                ret_val.update(value)
                gevent.sleep(0)

            finished = True
            gevent.sleep(check.frequency)
        except Timeout, t:
            if t is not timeout:
                raise # someone else getting timed out

            if not finished:
                log.exception("Did not finish %s" % check)

        return ret_val
        # TODO run the status processor