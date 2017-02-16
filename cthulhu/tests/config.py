import os
import ConfigParser

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../../tests/test.conf")


class ConfigNotFound(Exception):
    pass


class TestConfig(ConfigParser.SafeConfigParser):
    def __init__(self):
        ConfigParser.SafeConfigParser.__init__(self)

        self.path = DEFAULT_CONFIG_PATH

        if not os.path.exists(self.path):
            raise ConfigNotFound("Configuration not found at %s" % self.path)

        self.read(self.path)
