
Configuring Ceph
================

Calamari will configure Ceph to use our osd CRUSH location hook.
We do this to preserve an OSDs location in the CRUSH map when the osd restarts
if we've moved the OSD crush node with Calamari.


How it Works
------------

Our hook operates using the OSD cephx key and uses it to contact a Ceph MON.
Calamari stores information in the MON config-key store.


Failure Modes
-------------

If we detect that the hostname where an OSD is starting has changed from last reported location
we report the parent CRUSH node as host=current_hostname. This allows OSD hotplugging to work.

If we cannot get a MON to answer withing a short time period we report the parent CRUSH node as 
host=current_hostname. This allows OSDs to start without depending on the MON node.


Restoring Configuration
-----------------------

We preserve a copy of the cluster config on each node in /etc/ceph/{cluster_name}.conf.orig
Should you experince issues you can restore the config from there.
