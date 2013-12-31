

SALT_CONFIG_PATH = '/etc/salt/master'
SALT_RUN_PATH = '/var/run/salt/master'
# FIXME: this should be a function of the ceph.heartbeat schedule period which
# we should query from the salt pillar
FAVORITE_TIMEOUT_S = 60

DB_PATH = "sqlite:////var/lib/cthulhu/cthulhu.db"

LOG_PATH = "/var/log/calamari/cthulhu.log"

CTHULHU_RPC_URL = 'tcp://127.0.0.1:5050'
