#!/bin/bash

ID=$(lsb_release -i -s)

# ID is:
# Centos6.4: CentOS
# RHEL6: RedHatEnterpriseServer
# precise: Ubuntu
# wheezy: Debian

ret='debian'
if echo $ID | egrep -s -q -i 'centos|redhat'; then ret="rh"; fi
echo $ret
exit 0
