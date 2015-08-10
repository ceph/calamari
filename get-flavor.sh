#!/bin/bash

ID=$(lsb_release -i -s)
if [ $? != 0 ] ; then echo "$0: lsb_release failed..."; exit 1; fi
VERSION=$(lsb_release -r -s)

# ID is:
# Centos6.4: CentOS
# RHEL6: RedHatEnterpriseServer
# precise, trusty: Ubuntu
# wheezy: Debian
# SLES: SUSE Linux
# openSUSE: openSUSE project


case $ID in
    "CentOS"|"RedHatEnterpriseServer")
        case $VERSION in
            7.*) ret="rhel7" ;;
            6.*) ret="el6" ;;
            *) echo "$0: unhandled EL version $VERSION"; exit 1 ;;
        esac ;;
    "Ubuntu"|"Debian") ret="debian" ;;
    *SUSE*) ret="suse" ;;
    *) echo "$0: unhandled id $ID"; exit 1 ;;
esac

echo $ret
exit 0
