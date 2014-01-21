import salt

import salt.client

local = salt.client.LocalClient(c_path='dev/etc/salt/master')
print(local.cmd('cephmon', 'status-check.foo'))