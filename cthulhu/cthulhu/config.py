

SALT_CONFIG_PATH = './salt/etc/salt/master'
SALT_RUN_PATH = './salt/var/run/salt/master'
# FIXME: this should be a function of the ceph.heartbeat schedule period which
# we should query from the salt pillar
FAVORITE_TIMEOUT_S = 60

DB_PATH = "sqlite:///cthulhu.db"
