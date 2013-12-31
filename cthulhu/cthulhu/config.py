
import os
import ConfigParser


class ConfigNotFound(Exception):
    pass


DEFAULT_CONFIG_PATH = "/etc/calamari/calamari.conf"
CONFIG_PATH_VAR = "CALAMARI_CONFIG"


class CalamariConfig(ConfigParser.SafeConfigParser):
    def __init__(self):
        ConfigParser.SafeConfigParser.__init__(self)

        try:
            self.path = os.environ[CONFIG_PATH_VAR]
        except KeyError:
            self.path = DEFAULT_CONFIG_PATH

        if not os.path.exists(self.path):
            raise ConfigNotFound("Configuration not found at %s" % self.path)

        self.read(self.path)

    def set_and_write(self, section, option, value):
        self.set(section, option, value)
        self.write(open(self.path, 'w'))
