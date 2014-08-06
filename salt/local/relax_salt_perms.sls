# http://docs.saltstack.com/en/latest/ref/clientacl.html#permission-issues
# work around for https://github.com/saltstack/salt/issues/14768

allow_master_pillar_util_access:
    cmd.run:
        - name: chmod 0755 /var/cache/salt /var/cache/salt/master /var/cache/salt/jobs /var/run/salt
        - user: root
