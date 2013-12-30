import salt

import salt.client

local = salt.client.LocalClient(c_path='salt/etc/salt/master')
print(local.cmd('cephmon', 'status-check.foo'))