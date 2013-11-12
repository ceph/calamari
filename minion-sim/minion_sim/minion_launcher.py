import errno
import getpass
import os
import signal
import subprocess
from jinja2 import Template


PREFIX = 'figment'
DOMAIN = 'imagination.com'
ROOT = os.getcwd()

MINION_CONFIG_TEMPLATE = """
master: localhost
id: {{ HOSTNAME }}
user: {{ USER }}
pidfile: {{ ROOT }}/var/run/salt-minion.pid
pki_dir: {{ ROOT }}/etc/pki
cachedir: {{ ROOT }}/var/cache
log_file: {{ ROOT }}/var/log/salt/minion
sock_dir: /tmp
grains:
    fqdn: {{ FQDN}}
    localhost: {{ HOSTNAME }}
    host: {{ HOSTNAME }}
    nodename: {{ HOSTNAME }}
"""


class MinionLauncher(object):
    """
    Wrapper for a child/subprocess.

    Responsible for creating the filesystem tree for this salt
    minion, writing out a config file and then starting/stopping it.
    """
    def __init__(self, index):
        super(MinionLauncher, self).__init__()

        self.ps = None
        self.hostname = "{0}{1:03d}".format(PREFIX, index)
        self.fqdn = "{0}.{1}".format(self.hostname, DOMAIN)

        path = os.path.join(ROOT, self.hostname)

        try:
            os.makedirs(path)
            os.makedirs(os.path.join(path, 'var/run'))
            os.makedirs(os.path.join(path, 'etc/salt'))
        except OSError, e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise

        config_str = Template(MINION_CONFIG_TEMPLATE).render(
            HOSTNAME=self.hostname,
            USER=getpass.getuser(),
            ROOT=path,
            FQDN=self.fqdn
        )

        config_filename = os.path.join(path, 'etc/salt/minion')
        open(config_filename, 'w').write(config_str)

        self.cmdline = ['-c', os.path.dirname(config_filename)]

    def start(self):
        print "Calling salt_minion.start"
        self.ps = subprocess.Popen(['minion-child'] + self.cmdline)

    def stop(self):
        self.ps.send_signal(signal.SIGTERM)

    def join(self):
        self.ps.communicate()