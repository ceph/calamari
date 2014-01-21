import gevent
import os
import importlib
import sys

class PluginMonitor(gevent.greenlet.Greenlet):
    """
    Consumes output from plugins
    """

    def __init__(self, plugin_path):
        super(PluginMonitor, self).__init__()
        self.status_processors = {}
        self.status_checks = {}
        # TODO we probably need a different store for the crap we get from the checks and the stuff output by the processor
        self.plugin_data = {}
        self.plugin_path = plugin_path


    def get_data(self, plugin_name):
        return self.plugin_data.get(plugin_name)

    def load_status_check(self):
        self.load_module('status_check', self.status_checks)
       
    def load_status_processors(self):
        self.load_module('status_processor', self.status_processors)

    def load_module(self, class_name, index):
       """
       Try to load class_name from self.plugin_path, store in index keyed by module_name
       """
       for plugin in os.listdir(self.plugin_path):
           plugin = plugin.split('.')[0]
           if plugin in ('__init__', 'README'):
              continue
           # sys.stderr.write(plugin)
           try:
              index[plugin] = importlib.import_module('.'.join((plugin, class_name)))
              # sys.stderr.write(str(dir(index[plugin])))
           except ImportError:
              # TODO log failure here
              pass
               
    # We run this once we've gotten all the checks of a generation
    # TODO rename to run_status_processors and fix it to operate on a different data struct
    def run_plugins(self):
        # TODO we have gevent use it
        for name,x in self.status_processors.iteritems():
            # TODO what about failure
            self.plugin_data[name] = x.run()

    def run_status_checks(self):
        # TODO this isn't just as simple as run them every so often
        # we need to register them once we parse them
        # also don't bomb if we can't load a processor for these checks ?
        pass