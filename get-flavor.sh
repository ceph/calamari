#!/bin/bash

DESC=$(lsb_release -d -s)

ret='debian'
if echo $DESC | egrep -s -q -i 'centos|redhat'; then ret="rh"; fi
echo $ret
exit 0
