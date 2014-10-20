

:tocdepth: 3

API resources
=============

URL summary
-----------

========================================================== ===================================================== ========================================================================== === === ==== ===== ====== 
URL                                                        View                                                  Examples                                                                   GET PUT POST PATCH DELETE 
========================================================== ===================================================== ========================================================================== === === ==== ===== ====== 
api/v2/cluster/\<fsid\>/cli                                :ref:`Cli <CliViewSet>`                                                                                                                  Yes               
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster                                             :ref:`Cluster <ClusterViewSet>`                       :doc:`Example <api_example_api_v2_cluster>`                                Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<pk\>                                      :ref:`Cluster <ClusterViewSet>`                       :doc:`Example <api_example_api_v2_cluster__pk_>`                           Yes                Yes    
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/config                             :ref:`Config <ConfigViewSet>`                         :doc:`Example <api_example_api_v2_cluster__fsid__config>`                  Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/config/\<key\>                     :ref:`Config <ConfigViewSet>`                         :doc:`Example <api_example_api_v2_cluster__fsid__config__key_>`            Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/crush_map                          :ref:`Crush Map <CrushMapViewSet>`                                                                                               Yes     Yes               
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/crush_node                         :ref:`Crush Node <CrushNodeViewSet>`                                                                                             Yes     Yes               
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/crush_node/\<node_id\>             :ref:`Crush Node <CrushNodeViewSet>`                                                                                             Yes          Yes   Yes    
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/crush_rule_set                     :ref:`Crush Rule Set <CrushRuleSetViewSet>`           :doc:`Example <api_example_api_v2_cluster__fsid__crush_rule_set>`          Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/crush_rule                         :ref:`Crush Rule <CrushRuleViewSet>`                  :doc:`Example <api_example_api_v2_cluster__fsid__crush_rule>`              Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/server/\<fqdn\>/debug_job                           :ref:`Debug Job <DebugJob>`                                                                                                              Yes               
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/event                                               :ref:`Event <EventViewSet>`                           :doc:`Example <api_example_api_v2_event>`                                  Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/event                              :ref:`Event <EventViewSet>`                           :doc:`Example <api_example_api_v2_cluster__fsid__event>`                   Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/server/\<fqdn\>/event                               :ref:`Event <EventViewSet>`                           :doc:`Example <api_example_api_v2_server__fqdn__event>`                    Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/info                                                :ref:`Info <Info>`                                    :doc:`Example <api_example_api_v2_info>`                                   Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/log                                :ref:`Log Tail <LogTailViewSet>`                      :doc:`Example <api_example_api_v2_cluster__fsid__log>`                     Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/server/\<fqdn\>/log                                 :ref:`Log Tail <LogTailViewSet>`                      :doc:`Example <api_example_api_v2_server__fqdn__log>`                      Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/server/\<fqdn\>/log/\<log_path\>                    :ref:`Log Tail <LogTailViewSet>`                      :doc:`Example <api_example_api_v2_server__fqdn__log__log_path_>`           Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/mon                                :ref:`Mon <MonViewSet>`                                                                                                          Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/mon/\<mon_id\>                     :ref:`Mon <MonViewSet>`                                                                                                          Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/mon/\<mon_id\>/status              :ref:`Mon <MonViewSet>`                                                                                                          Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/osd_config                         :ref:`Osd Config <OsdConfigViewSet>`                                                                                             Yes          Yes          
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/osd                                :ref:`Osd <OsdViewSet>`                               :doc:`Example <api_example_api_v2_cluster__fsid__osd>`                     Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/osd/\<osd_id\>                     :ref:`Osd <OsdViewSet>`                               :doc:`Example <api_example_api_v2_cluster__fsid__osd__osd_id_>`            Yes          Yes          
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/osd /command                       :ref:`Osd <OsdViewSet>`                                                                                                          Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/osd/\<osd_id\>/command             :ref:`Osd <OsdViewSet>`                                                                                                          Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/osd/\<osd_id\>/command/\<command\> :ref:`Osd <OsdViewSet>`                                                                                                          Yes     Yes               
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/pool                               :ref:`Pool <PoolViewSet>`                             :doc:`Example <api_example_api_v2_cluster__fsid__pool>`                    Yes     Yes               
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/pool/\<pool_id\>                   :ref:`Pool <PoolViewSet>`                             :doc:`Example <api_example_api_v2_cluster__fsid__pool__pool_id_>`          Yes          Yes   Yes    
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/request/\<request_id\>/cancel                       :ref:`Request <RequestViewSet>`                                                                                                          Yes               
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/request/\<request_id\>                              :ref:`Request <RequestViewSet>`                                                                                                  Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/request                                             :ref:`Request <RequestViewSet>`                                                                                                  Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/request/\<request_id\>             :ref:`Request <RequestViewSet>`                       :doc:`Example <api_example_api_v2_cluster__fsid__request__request_id_>`    Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/request                            :ref:`Request <RequestViewSet>`                       :doc:`Example <api_example_api_v2_cluster__fsid__request>`                 Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/key                                                 :ref:`Salt Key <SaltKeyViewSet>`                      :doc:`Example <api_example_api_v2_key>`                                    Yes          Yes   Yes    
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/key/\<minion_id\>                                   :ref:`Salt Key <SaltKeyViewSet>`                      :doc:`Example <api_example_api_v2_key__minion_id_>`                        Yes          Yes   Yes    
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/server                             :ref:`Server (within cluster) <ServerClusterViewSet>` :doc:`Example <api_example_api_v2_cluster__fsid__server>`                  Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/server/\<fqdn\>                    :ref:`Server (within cluster) <ServerClusterViewSet>` :doc:`Example <api_example_api_v2_cluster__fsid__server__fqdn_>`           Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/server                                              :ref:`Server <ServerViewSet>`                         :doc:`Example <api_example_api_v2_server>`                                 Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/server/\<fqdn\>                                     :ref:`Server <ServerViewSet>`                         :doc:`Example <api_example_api_v2_server__fqdn_>`                          Yes                Yes    
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/server/\<fqdn\>/grains                              :ref:`Server <ServerViewSet>`                         :doc:`Example <api_example_api_v2_server__fqdn__grains>`                   Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/sync_object                        :ref:`Sync Object <SyncObject>`                       :doc:`Example <api_example_api_v2_cluster__fsid__sync_object>`             Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/cluster/\<fsid\>/sync_object/\<sync_type\>          :ref:`Sync Object <SyncObject>`                       :doc:`Example <api_example_api_v2_cluster__fsid__sync_object__sync_type_>` Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/user                                                :ref:`User <UserViewSet>`                             :doc:`Example <api_example_api_v2_user>`                                   Yes     Yes               
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/user/\<pk\>                                         :ref:`User <UserViewSet>`                             :doc:`Example <api_example_api_v2_user__pk_>`                              Yes Yes      Yes   Yes    
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/grains                                              :ref:`Grains <grains>`                                :doc:`Example <api_example_api_v2_grains>`                                 Yes                       
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/auth/login                                          :ref:`Login <login>`                                  :doc:`Example <api_example_api_v2_auth_login>`                             Yes     Yes               
---------------------------------------------------------- ----------------------------------------------------- -------------------------------------------------------------------------- --- --- ---- ----- ------ 
api/v2/auth/logout                                         :ref:`Logout <logout>`                                                                                                           Yes     Yes               
========================================================== ===================================================== ========================================================================== === === ==== ===== ====== 


API reference
-------------



.. _CliViewSet:

Cli
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Access the `ceph` CLI tool remotely.

To achieve the same result as running "ceph osd dump" at a shell, an
API consumer may POST an object in either of the following formats:

::

    {'command': ['osd', 'dump']}

    {'command': 'osd dump'}


The response will be a 200 status code if the command executed, regardless
of whether it was successful, to check the result of the command itself
read the ``status`` attribute of the returned data.

The command will be executed on the first available mon server, retrying
on subsequent mon servers if no response is received.  Due to this retry
behaviour, it is possible for the command to be run more than once in
rare cases; since most ceph commands are idempotent this is usually
not a problem.
    

URLs
____

========================================================================== === === ==== ===== ====== 
URL                                                                        GET PUT POST PATCH DELETE 
========================================================================== === === ==== ===== ====== 
:doc:`api/v2/cluster/\<fsid\>/cli <api_example_api_v2_cluster__fsid__cli>`         Yes               
========================================================================== === === ==== ===== ====== 


Fields
______

====== ======= ======== ====== ====== ============== 
Name   Type    Readonly Create Modify Description    
====== ======= ======== ====== ====== ============== 
out    string  False                  Standard out   
------ ------- -------- ------ ------ -------------- 
err    string  False                  Standard error 
------ ------- -------- ------ ------ -------------- 
status integer False                  Exit code      
====== ======= ======== ====== ====== ============== 



.. _ClusterViewSet:

Cluster
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


A Ceph cluster, uniquely identified by its FSID.  All Ceph services such
as OSDs and mons are namespaced within a cluster.  Servers may host services
for more than one cluster, although usually they only hold one.

Note that the ``name`` attribute of a Ceph cluster has no uniqueness,
code consuming this API should always use the FSID to identify clusters.

Using the DELETE verb on a Ceph cluster will cause the Calamari server
to drop its records of the cluster and services within the cluster.  However,
if the cluster still exists on servers managed by Calamari, it will be immediately
redetected: only use DELETE on clusters which really no longer exist.
    

URLs
____

============================================================== === === ==== ===== ====== 
URL                                                            GET PUT POST PATCH DELETE 
============================================================== === === ==== ===== ====== 
:doc:`api/v2/cluster <api_example_api_v2_cluster>`             Yes                       
-------------------------------------------------------------- --- --- ---- ----- ------ 
:doc:`api/v2/cluster/\<pk\> <api_example_api_v2_cluster__pk_>` Yes                Yes    
============================================================== === === ==== ===== ====== 


Fields
______

=========== ======== ======== ====== ====== ======================================================================= 
Name        Type     Readonly Create Modify Description                                                             
=========== ======== ======== ====== ====== ======================================================================= 
update_time datetime False                  The time at which the last status update from this cluster was received 
----------- -------- -------- ------ ------ ----------------------------------------------------------------------- 
id          field    True                   The FSID of the cluster, universally unique                             
----------- -------- -------- ------ ------ ----------------------------------------------------------------------- 
name        field    True                   Human readable cluster name, not a unique identifier                    
=========== ======== ======== ====== ====== ======================================================================= 



.. _ConfigViewSet:

Config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Configuration settings from a Ceph Cluster.
    

URLs
____

============================================================================================== === === ==== ===== ====== 
URL                                                                                            GET PUT POST PATCH DELETE 
============================================================================================== === === ==== ===== ====== 
:doc:`api/v2/cluster/\<fsid\>/config <api_example_api_v2_cluster__fsid__config>`               Yes                       
---------------------------------------------------------------------------------------------- --- --- ---- ----- ------ 
:doc:`api/v2/cluster/\<fsid\>/config/\<key\> <api_example_api_v2_cluster__fsid__config__key_>` Yes                       
============================================================================================== === === ==== ===== ====== 


Fields
______

===== ====== ======== ====== ====== ========================================= 
Name  Type   Readonly Create Modify Description                               
===== ====== ======== ====== ====== ========================================= 
key   string False                  Name of the configuration setting         
----- ------ -------- ------ ------ ----------------------------------------- 
value string False                  Current value of the setting, as a string 
===== ====== ======== ====== ====== ========================================= 



.. _CrushMapViewSet:

Crush Map
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Allows retrieval and replacement of a crushmap as a whole
    

URLs
____

====================================================================================== === === ==== ===== ====== 
URL                                                                                    GET PUT POST PATCH DELETE 
====================================================================================== === === ==== ===== ====== 
:doc:`api/v2/cluster/\<fsid\>/crush_map <api_example_api_v2_cluster__fsid__crush_map>` Yes     Yes               
====================================================================================== === === ==== ===== ====== 


Fields
______

*No field data available*


.. _CrushNodeViewSet:

Crush Node
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


The CRUSH algorithm distributes data objects among storage devices according to a per-device weight value, approximating a uniform probability distribution. CRUSH distributes objects and their replicas according to the hierarchical cluster map you define. Your CRUSH map represents the available storage devices and the logical elements that contain them.
    

URLs
____

============================================================================================================== === === ==== ===== ====== 
URL                                                                                                            GET PUT POST PATCH DELETE 
============================================================================================================== === === ==== ===== ====== 
:doc:`api/v2/cluster/\<fsid\>/crush_node <api_example_api_v2_cluster__fsid__crush_node>`                       Yes     Yes               
-------------------------------------------------------------------------------------------------------------- --- --- ---- ----- ------ 
:doc:`api/v2/cluster/\<fsid\>/crush_node/\<node_id\> <api_example_api_v2_cluster__fsid__crush_node__node_id_>` Yes          Yes   Yes    
============================================================================================================== === === ==== ===== ====== 


Fields
______

=========== =============== ======== ======= ======= ================================================================================================================================================================= 
Name        Type            Readonly Create  Modify  Description                                                                                                                                                       
=========== =============== ======== ======= ======= ================================================================================================================================================================= 
bucket_type string          False    Allowed Allowed Buckets facilitate a hierarchy of nodes and leaves. Node (or non-leaf) buckets typically represent physical locations in a hierarchy. e.g. host, rack, datacenter 
----------- --------------- -------- ------- ------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------- 
name        string          False    Allowed Allowed unique name                                                                                                                                                       
----------- --------------- -------- ------- ------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------- 
id          integer         False    Allowed         unique ID expressed as an integer (optional)                                                                                                                      
----------- --------------- -------- ------- ------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------- 
weight      float           False                    the relative capacity/capability of the item(s)                                                                                                                   
----------- --------------- -------- ------- ------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------- 
alg         multiple choice False                    bucket algorithm                                                                                                                                                  
----------- --------------- -------- ------- ------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------- 
hash        integer         False                    hash algorithm                                                                                                                                                    
----------- --------------- -------- ------- ------- ----------------------------------------------------------------------------------------------------------------------------------------------------------------- 
items       field           False    Allowed Allowed A bucket may have one or more items. The items may consist of node buckets or leaves. Items may have a weight that reflects the relative weight of the item.      
=========== =============== ======== ======= ======= ================================================================================================================================================================= 



.. _CrushRuleSetViewSet:

Crush Rule Set
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


A CRUSH rule is used by Ceph to decide where to locate placement groups on OSDs.
    

URLs
____

================================================================================================ === === ==== ===== ====== 
URL                                                                                              GET PUT POST PATCH DELETE 
================================================================================================ === === ==== ===== ====== 
:doc:`api/v2/cluster/\<fsid\>/crush_rule_set <api_example_api_v2_cluster__fsid__crush_rule_set>` Yes                       
================================================================================================ === === ==== ===== ====== 


Fields
______

===== ======= ======== ====== ====== =========== 
Name  Type    Readonly Create Modify Description 
===== ======= ======== ====== ====== =========== 
id    integer False                              
----- ------- -------- ------ ------ ----------- 
rules field   False                              
===== ======= ======== ====== ====== =========== 



.. _CrushRuleViewSet:

Crush Rule
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


A CRUSH ruleset is a collection of CRUSH rules which are applied
together to a pool.
    

URLs
____

======================================================================================== === === ==== ===== ====== 
URL                                                                                      GET PUT POST PATCH DELETE 
======================================================================================== === === ==== ===== ====== 
:doc:`api/v2/cluster/\<fsid\>/crush_rule <api_example_api_v2_cluster__fsid__crush_rule>` Yes                       
======================================================================================== === === ==== ===== ====== 


Fields
______

========= ======= ======== ====== ====== ================================================================================ 
Name      Type    Readonly Create Modify Description                                                                      
========= ======= ======== ====== ====== ================================================================================ 
id        integer False                                                                                                   
--------- ------- -------- ------ ------ -------------------------------------------------------------------------------- 
name      string  False                  Human readable name                                                              
--------- ------- -------- ------ ------ -------------------------------------------------------------------------------- 
ruleset   integer False                  ID of the CRUSH ruleset of which this rule is a member                           
--------- ------- -------- ------ ------ -------------------------------------------------------------------------------- 
type      string  False                  Data redundancy type (one of replicated, erasure)                                
--------- ------- -------- ------ ------ -------------------------------------------------------------------------------- 
min_size  integer False                  If a pool makes more replicas than this number, CRUSH will NOT select this rule  
--------- ------- -------- ------ ------ -------------------------------------------------------------------------------- 
max_size  integer False                  If a pool makes fewer replicas than this number, CRUSH will NOT select this rule 
--------- ------- -------- ------ ------ -------------------------------------------------------------------------------- 
steps     field   True                   List of operations used to select OSDs                                           
--------- ------- -------- ------ ------ -------------------------------------------------------------------------------- 
osd_count integer False                  Number of OSDs which are used for data placement                                 
========= ======= ======== ====== ====== ================================================================================ 



.. _DebugJob:

Debug Job
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


For debugging and automated testing only.
    

URLs
____

==================================================================================== === === ==== ===== ====== 
URL                                                                                  GET PUT POST PATCH DELETE 
==================================================================================== === === ==== ===== ====== 
:doc:`api/v2/server/\<fqdn\>/debug_job <api_example_api_v2_server__fqdn__debug_job>`         Yes               
==================================================================================== === === ==== ===== ====== 


Fields
______

*No field data available*


.. _EventViewSet:

Event
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Events generated by Calamari server in response to messages from
servers and Ceph clusters.  This resource is paginated.

Note that events are not visible synchronously with respect to
all other API resources.  For example, you might read the OSD
map, see an OSD is down, then quickly read the events and find
that the event about the OSD going down is not visible yet (though
it would appear very soon after).

The ``severity`` attribute mainly follows a typical INFO, WARN, ERROR
hierarchy.  However, we have an additional level between INFO and WARN
called RECOVERY.  Where something going bad in the system is usually
a WARN message, the opposite state transition is usually a RECOVERY
message.

This resource supports "more severe than" filtering on the severity
attribute.  Pass the desired severity threshold as a URL parameter
in a GET, such as ``?severity=RECOVERY`` to show everything but INFO.

    

URLs
____

============================================================================== === === ==== ===== ====== 
URL                                                                            GET PUT POST PATCH DELETE 
============================================================================== === === ==== ===== ====== 
:doc:`api/v2/event <api_example_api_v2_event>`                                 Yes                       
------------------------------------------------------------------------------ --- --- ---- ----- ------ 
:doc:`api/v2/cluster/\<fsid\>/event <api_example_api_v2_cluster__fsid__event>` Yes                       
------------------------------------------------------------------------------ --- --- ---- ----- ------ 
:doc:`api/v2/server/\<fqdn\>/event <api_example_api_v2_server__fqdn__event>`   Yes                       
============================================================================== === === ==== ===== ====== 


Fields
______

======== ======== ======== ====== ====== =========================================== 
Name     Type     Readonly Create Modify Description                                 
======== ======== ======== ====== ====== =========================================== 
when     datetime False                  Time at which event was generated           
-------- -------- -------- ------ ------ ------------------------------------------- 
severity field    True                   One of CRITICAL,ERROR,WARNING,RECOVERY,INFO 
-------- -------- -------- ------ ------ ------------------------------------------- 
message  string   False                  One line human readable description         
======== ======== ======== ====== ====== =========================================== 



.. _Info:

Info
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Provides metadata about the installation of Calamari server in use
    

URLs
____

============================================ === === ==== ===== ====== 
URL                                          GET PUT POST PATCH DELETE 
============================================ === === ==== ===== ====== 
:doc:`api/v2/info <api_example_api_v2_info>` Yes                       
============================================ === === ==== ===== ====== 


Fields
______

================ ====== ======== ====== ====== ================================================= 
Name             Type   Readonly Create Modify Description                                       
================ ====== ======== ====== ====== ================================================= 
version          string False                  Calamari server version                           
---------------- ------ -------- ------ ------ ------------------------------------------------- 
license          string False                  Calamari license metadata                         
---------------- ------ -------- ------ ------ ------------------------------------------------- 
registered       string False                  Calamari registration metadata                    
---------------- ------ -------- ------ ------ ------------------------------------------------- 
hostname         string False                  Hostname of Calamari server                       
---------------- ------ -------- ------ ------ ------------------------------------------------- 
fqdn             string False                  Fully qualified domain name of Calamari server    
---------------- ------ -------- ------ ------ ------------------------------------------------- 
ipaddr           string False                  IP address of Calamari server                     
---------------- ------ -------- ------ ------ ------------------------------------------------- 
bootstrap_url    string False                  URL to minion bootstrap script                    
---------------- ------ -------- ------ ------ ------------------------------------------------- 
bootstrap_rhel   string False                  Minion bootstrap command line for Red Hat systems 
---------------- ------ -------- ------ ------ ------------------------------------------------- 
bootstrap_ubuntu string False                  Minion bootstrap command line for Ubuntu systems  
================ ====== ======== ====== ====== ================================================= 



.. _LogTailViewSet:

Log Tail
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


A primitive remote log viewer.

Logs are retrieved on demand from the Ceph servers, so this resource will return a 503 error if no suitable
server is available to get the logs.

GETs take an optional ``lines`` parameter for the number of lines to retrieve.
    

URLs
____

================================================================================================ === === ==== ===== ====== 
URL                                                                                              GET PUT POST PATCH DELETE 
================================================================================================ === === ==== ===== ====== 
:doc:`api/v2/cluster/\<fsid\>/log <api_example_api_v2_cluster__fsid__log>`                       Yes                       
------------------------------------------------------------------------------------------------ --- --- ---- ----- ------ 
:doc:`api/v2/server/\<fqdn\>/log <api_example_api_v2_server__fqdn__log>`                         Yes                       
------------------------------------------------------------------------------------------------ --- --- ---- ----- ------ 
:doc:`api/v2/server/\<fqdn\>/log/\<log_path\> <api_example_api_v2_server__fqdn__log__log_path_>` Yes                       
================================================================================================ === === ==== ===== ====== 


Fields
______

===== ====== ======== ====== ====== =========== 
Name  Type   Readonly Create Modify Description 
===== ====== ======== ====== ====== =========== 
lines string False                              
===== ====== ======== ====== ====== =========== 



.. _MonViewSet:

Mon
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Ceph monitor services.

Note that the ID used to retrieve a specific mon using this API resource is
the monitor *name* as opposed to the monitor *rank*.

The quorum status reported here is based on the last mon status reported by
the Ceph cluster, and also the status of each mon daemon queried by Calamari.

For debugging mons which are failing to join the cluster, it may be
useful to show users data from the /status sub-url, which returns the
"mon_status" output from the daemon.

    

URLs
____

============================================================================================================ === === ==== ===== ====== 
URL                                                                                                          GET PUT POST PATCH DELETE 
============================================================================================================ === === ==== ===== ====== 
:doc:`api/v2/cluster/\<fsid\>/mon <api_example_api_v2_cluster__fsid__mon>`                                   Yes                       
------------------------------------------------------------------------------------------------------------ --- --- ---- ----- ------ 
:doc:`api/v2/cluster/\<fsid\>/mon/\<mon_id\> <api_example_api_v2_cluster__fsid__mon__mon_id_>`               Yes                       
------------------------------------------------------------------------------------------------------------ --- --- ---- ----- ------ 
:doc:`api/v2/cluster/\<fsid\>/mon/\<mon_id\>/status <api_example_api_v2_cluster__fsid__mon__mon_id__status>` Yes                       
============================================================================================================ === === ==== ===== ====== 


Fields
______

========= ======= ======== ====== ====== ============================================= 
Name      Type    Readonly Create Modify Description                                   
========= ======= ======== ====== ====== ============================================= 
name      string  False                  Human readable name                           
--------- ------- -------- ------ ------ --------------------------------------------- 
rank      integer False                  Unique of the mon within the cluster          
--------- ------- -------- ------ ------ --------------------------------------------- 
in_quorum boolean False                  True if the mon is a member of current quorum 
--------- ------- -------- ------ ------ --------------------------------------------- 
server    string  False                  FQDN of server running the OSD                
--------- ------- -------- ------ ------ --------------------------------------------- 
addr      string  False                  IP address of monitor service                 
========= ======= ======== ====== ====== ============================================= 



.. _OsdConfigViewSet:

Osd Config
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Manage flags in the OsdMap
    

URLs
____

======================================================================================== === === ==== ===== ====== 
URL                                                                                      GET PUT POST PATCH DELETE 
======================================================================================== === === ==== ===== ====== 
:doc:`api/v2/cluster/\<fsid\>/osd_config <api_example_api_v2_cluster__fsid__osd_config>` Yes          Yes          
======================================================================================== === === ==== ===== ====== 


Fields
______

============ ======= ======== ====== ======= ================================================================================================================== 
Name         Type    Readonly Create Modify  Description                                                                                                        
============ ======= ======== ====== ======= ================================================================================================================== 
pause        boolean False           Allowed Disable IO requests to all OSDs in cluster                                                                         
------------ ------- -------- ------ ------- ------------------------------------------------------------------------------------------------------------------ 
noup         boolean False           Allowed Prevent OSDs from automatically getting marked as Up by the monitors. This setting is useful for troubleshooting   
------------ ------- -------- ------ ------- ------------------------------------------------------------------------------------------------------------------ 
nodown       boolean False           Allowed Prevent OSDs from automatically getting marked as Down by the monitors. This setting is useful for troubleshooting 
------------ ------- -------- ------ ------- ------------------------------------------------------------------------------------------------------------------ 
noout        boolean False           Allowed Prevent Down OSDs from being marked as out                                                                         
------------ ------- -------- ------ ------- ------------------------------------------------------------------------------------------------------------------ 
noin         boolean False           Allowed Prevent OSDs from booting OSDs from being marked as IN. Will cause cluster health to be set to WARNING             
------------ ------- -------- ------ ------- ------------------------------------------------------------------------------------------------------------------ 
nobackfill   boolean False           Allowed Disable backfill operations on cluster                                                                             
------------ ------- -------- ------ ------- ------------------------------------------------------------------------------------------------------------------ 
norecover    boolean False           Allowed Disable replication of Placement Groups                                                                            
------------ ------- -------- ------ ------- ------------------------------------------------------------------------------------------------------------------ 
noscrub      boolean False           Allowed Disables automatic periodic scrub operations on OSDs. May still be initiated on demand                             
------------ ------- -------- ------ ------- ------------------------------------------------------------------------------------------------------------------ 
nodeep-scrub boolean False           Allowed Disables automatic periodic deep scrub operations on OSDs. May still be initiated on demand                        
============ ======= ======== ====== ======= ================================================================================================================== 



.. _OsdViewSet:

Osd
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Manage Ceph OSDs.

Apply ceph commands to an OSD by doing a POST with no data to
api/v2/cluster/<fsid>/osd/<osd_id>/command/<command>
where <command> is one of ("scrub", "deep-scrub", "repair")

e.g. Initiate a scrub on OSD 0 by POSTing {} to api/v2/cluster/<fsid>/osd/0/command/scrub

Filtering is available on this resource:

::

    # Pass a ``pool`` URL parameter set to a pool ID to filter by pool, like this:
    /api/v2/cluster/<fsid>/osd?pool=1

    # Pass a series of ``id__in[]`` parameters to specify a list of OSD IDs
    # that you wish to receive.
    /api/v2/cluster/<fsid>/osd?id__in[]=2&id__in[]=3

    

URLs
____

==================================================================================================================================== === === ==== ===== ====== 
URL                                                                                                                                  GET PUT POST PATCH DELETE 
==================================================================================================================================== === === ==== ===== ====== 
:doc:`api/v2/cluster/\<fsid\>/osd <api_example_api_v2_cluster__fsid__osd>`                                                           Yes                       
------------------------------------------------------------------------------------------------------------------------------------ --- --- ---- ----- ------ 
:doc:`api/v2/cluster/\<fsid\>/osd/\<osd_id\> <api_example_api_v2_cluster__fsid__osd__osd_id_>`                                       Yes          Yes          
------------------------------------------------------------------------------------------------------------------------------------ --- --- ---- ----- ------ 
:doc:`api/v2/cluster/\<fsid\>/osd /command <api_example_api_v2_cluster__fsid__osd _command>`                                         Yes                       
------------------------------------------------------------------------------------------------------------------------------------ --- --- ---- ----- ------ 
:doc:`api/v2/cluster/\<fsid\>/osd/\<osd_id\>/command <api_example_api_v2_cluster__fsid__osd__osd_id__command>`                       Yes                       
------------------------------------------------------------------------------------------------------------------------------------ --- --- ---- ----- ------ 
:doc:`api/v2/cluster/\<fsid\>/osd/\<osd_id\>/command/\<command\> <api_example_api_v2_cluster__fsid__osd__osd_id__command__command_>` Yes     Yes               
==================================================================================================================================== === === ==== ===== ====== 


Fields
______

============== =========== ======== ====== ======= ============================================================================ 
Name           Type        Readonly Create Modify  Description                                                                  
============== =========== ======== ====== ======= ============================================================================ 
uuid           uuid string True                    Globally unique ID for this OSD                                              
-------------- ----------- -------- ------ ------- ---------------------------------------------------------------------------- 
up             boolean     False           Allowed Whether the OSD is running from the point of view of the rest of the cluster 
-------------- ----------- -------- ------ ------- ---------------------------------------------------------------------------- 
in             boolean     False           Allowed Whether the OSD is 'in' the set of OSDs which will be used to store data     
-------------- ----------- -------- ------ ------- ---------------------------------------------------------------------------- 
id             integer     True                    ID of this OSD within this cluster                                           
-------------- ----------- -------- ------ ------- ---------------------------------------------------------------------------- 
reweight       float       False           Allowed CRUSH weight factor                                                          
-------------- ----------- -------- ------ ------- ---------------------------------------------------------------------------- 
server         string      True                    FQDN of server this OSD was last running on                                  
-------------- ----------- -------- ------ ------- ---------------------------------------------------------------------------- 
pools          field       True                    List of pool IDs which use this OSD for storage                              
-------------- ----------- -------- ------ ------- ---------------------------------------------------------------------------- 
valid_commands string      True                    List of commands that can be applied to this OSD                             
-------------- ----------- -------- ------ ------- ---------------------------------------------------------------------------- 
public_addr    string      True                    Public/frontend IP address                                                   
-------------- ----------- -------- ------ ------- ---------------------------------------------------------------------------- 
cluster_addr   string      True                    Cluster/backend IP address                                                   
============== =========== ======== ====== ======= ============================================================================ 



.. _PoolViewSet:

Pool
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Manage Ceph storage pools.

To get the default values which will be used for any fields omitted from a POST, do
a GET with the ?defaults argument.  The returned pool object will contain all attributes,
but those without static defaults will be set to null.

    

URLs
____

================================================================================================== === === ==== ===== ====== 
URL                                                                                                GET PUT POST PATCH DELETE 
================================================================================================== === === ==== ===== ====== 
:doc:`api/v2/cluster/\<fsid\>/pool <api_example_api_v2_cluster__fsid__pool>`                       Yes     Yes               
-------------------------------------------------------------------------------------------------- --- --- ---- ----- ------ 
:doc:`api/v2/cluster/\<fsid\>/pool/\<pool_id\> <api_example_api_v2_cluster__fsid__pool__pool_id_>` Yes          Yes   Yes    
================================================================================================== === === ==== ===== ====== 


Fields
______

===================== ======= ======== ======== ======= ============================================================================================================= 
Name                  Type    Readonly Create   Modify  Description                                                                                                   
===================== ======= ======== ======== ======= ============================================================================================================= 
name                  string  False    Required Allowed Human readable name of the pool, maychange over the pools lifetime at user request.                           
--------------------- ------- -------- -------- ------- ------------------------------------------------------------------------------------------------------------- 
id                    string  False                     Unique numeric ID                                                                                             
--------------------- ------- -------- -------- ------- ------------------------------------------------------------------------------------------------------------- 
size                  integer False    Allowed  Allowed Replication factor                                                                                            
--------------------- ------- -------- -------- ------- ------------------------------------------------------------------------------------------------------------- 
pg_num                integer False    Required Allowed Number of placement groups in this pool                                                                       
--------------------- ------- -------- -------- ------- ------------------------------------------------------------------------------------------------------------- 
crush_ruleset         integer False    Allowed  Allowed CRUSH ruleset in use                                                                                          
--------------------- ------- -------- -------- ------- ------------------------------------------------------------------------------------------------------------- 
min_size              integer False    Allowed  Allowed Minimum number of replicas required for I/O; clamped to 'size' if greater; 0 defaults to 'size - int(size/2)' 
--------------------- ------- -------- -------- ------- ------------------------------------------------------------------------------------------------------------- 
crash_replay_interval integer False    Allowed  Allowed Number of seconds to allow clients to replay acknowledged, but uncommitted requests                           
--------------------- ------- -------- -------- ------- ------------------------------------------------------------------------------------------------------------- 
pgp_num               integer False    Allowed  Allowed Effective number of placement groups to use when calculating data placement                                   
--------------------- ------- -------- -------- ------- ------------------------------------------------------------------------------------------------------------- 
hashpspool            boolean False    Allowed  Allowed Enable HASHPSPOOL flag                                                                                        
--------------------- ------- -------- -------- ------- ------------------------------------------------------------------------------------------------------------- 
full                  boolean False                     True if the pool is full                                                                                      
--------------------- ------- -------- -------- ------- ------------------------------------------------------------------------------------------------------------- 
quota_max_objects     integer False    Allowed  Allowed Quota limit on object count (0 is unlimited)                                                                  
--------------------- ------- -------- -------- ------- ------------------------------------------------------------------------------------------------------------- 
quota_max_bytes       integer False    Allowed  Allowed Quota limit on usage in bytes (0 is unlimited)                                                                
===================== ======= ======== ======== ======= ============================================================================================================= 



.. _RequestViewSet:

Request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Calamari server requests, tracking long-running operations on the Calamari server.  Some
API resources return a ``202 ACCEPTED`` response with a request ID, which you can use with
this resource to learn about progress and completion of an operation.  This resource is
paginated.

May optionally filter by state by passing a ``?state=<state>`` GET parameter, where
state is one of 'complete', 'submitted'.

The returned records are ordered by the 'requested_at' attribute, in descending order (i.e.
the first page of results contains the most recent requests).

To cancel a request while it is running, send an empty POST to ``request/<request id>/cancel``.
    

URLs
____

============================================================================================================== === === ==== ===== ====== 
URL                                                                                                            GET PUT POST PATCH DELETE 
============================================================================================================== === === ==== ===== ====== 
:doc:`api/v2/request/\<request_id\>/cancel <api_example_api_v2_request__request_id__cancel>`                           Yes               
-------------------------------------------------------------------------------------------------------------- --- --- ---- ----- ------ 
:doc:`api/v2/request/\<request_id\> <api_example_api_v2_request__request_id_>`                                 Yes                       
-------------------------------------------------------------------------------------------------------------- --- --- ---- ----- ------ 
:doc:`api/v2/request <api_example_api_v2_request>`                                                             Yes                       
-------------------------------------------------------------------------------------------------------------- --- --- ---- ----- ------ 
:doc:`api/v2/cluster/\<fsid\>/request/\<request_id\> <api_example_api_v2_cluster__fsid__request__request_id_>` Yes                       
-------------------------------------------------------------------------------------------------------------- --- --- ---- ----- ------ 
:doc:`api/v2/cluster/\<fsid\>/request <api_example_api_v2_cluster__fsid__request>`                             Yes                       
============================================================================================================== === === ==== ===== ====== 


Fields
______

============= ======== ======== ====== ====== ========================================================================================================================== 
Name          Type     Readonly Create Modify Description                                                                                                                
============= ======== ======== ====== ====== ========================================================================================================================== 
id            string   False                  A globally unique ID for this request                                                                                      
------------- -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
state         string   False                  One of 'complete', 'submitted'                                                                                             
------------- -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
error         boolean  False                  True if the request completed unsuccessfully                                                                               
------------- -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
error_message string   False                  Human readable string describing failure if ``error`` is True                                                              
------------- -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
headline      string   False                  Single sentence human readable description of the request                                                                  
------------- -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
status        string   False                  Single sentence human readable description of the request's current activity, if it has more than one stage.  May be null. 
------------- -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
requested_at  datetime False                  Time at which the request was received by calamari server                                                                  
------------- -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
completed_at  datetime False                  Time at which the request completed, may be null.                                                                          
============= ======== ======== ====== ====== ========================================================================================================================== 



.. _SaltKeyViewSet:

Salt Key
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Ceph servers authentication with the Calamari using a key pair.  Before
Calamari accepts messages from a server, the server's key must be accepted.
    

URLs
____

==================================================================== === === ==== ===== ====== 
URL                                                                  GET PUT POST PATCH DELETE 
==================================================================== === === ==== ===== ====== 
:doc:`api/v2/key <api_example_api_v2_key>`                           Yes          Yes   Yes    
-------------------------------------------------------------------- --- --- ---- ----- ------ 
:doc:`api/v2/key/\<minion_id\> <api_example_api_v2_key__minion_id_>` Yes          Yes   Yes    
==================================================================== === === ==== ===== ====== 


Fields
______

====== ====== ======== ====== ======= ============================================= 
Name   Type   Readonly Create Modify  Description                                   
====== ====== ======== ====== ======= ============================================= 
id     string False                   The minion ID, usually equal to a host's FQDN 
------ ------ -------- ------ ------- --------------------------------------------- 
status string False           Allowed One of 'accepted', 'rejected' or 'pre'        
====== ====== ======== ====== ======= ============================================= 



.. _ServerClusterViewSet:

Server (within cluster)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


View of servers within a particular cluster.

Use the global server view for DELETE operations (there is no
concept of deleting a server from a cluster, only deleting
all record of it from any/all clusters).
    

URLs
____

================================================================================================ === === ==== ===== ====== 
URL                                                                                              GET PUT POST PATCH DELETE 
================================================================================================ === === ==== ===== ====== 
:doc:`api/v2/cluster/\<fsid\>/server <api_example_api_v2_cluster__fsid__server>`                 Yes                       
------------------------------------------------------------------------------------------------ --- --- ---- ----- ------ 
:doc:`api/v2/cluster/\<fsid\>/server/\<fqdn\> <api_example_api_v2_cluster__fsid__server__fqdn_>` Yes                       
================================================================================================ === === ==== ===== ====== 


Fields
______

============== ======== ======== ====== ====== ========================================================================================================================== 
Name           Type     Readonly Create Modify Description                                                                                                                
============== ======== ======== ====== ====== ========================================================================================================================== 
fqdn           string   False                  Fully qualified domain name                                                                                                
-------------- -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
hostname       string   False                  Unqualified hostname                                                                                                       
-------------- -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
services       field    False                  List of Ceph services seenon this server                                                                                   
-------------- -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
frontend_addr  string   False                                                                                                                                             
-------------- -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
backend_addr   string   False                                                                                                                                             
-------------- -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
frontend_iface string   False                                                                                                                                             
-------------- -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
backend_iface  string   False                                                                                                                                             
-------------- -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
managed        boolean  False                  True if this server is under Calamari server's control, falseif the server's existence was inferred via Ceph cluster maps. 
-------------- -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
last_contact   datetime False                  The time at which this server last communicated with the Calamariserver.  This is always null for unmanaged servers        
-------------- -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
boot_time      datetime False                  The time at which this server booted. This is always null for unmanaged servers                                            
-------------- -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
ceph_version   string   False                  The version of Ceph installed.  This is always null for unmanaged servers.                                                 
============== ======== ======== ====== ====== ========================================================================================================================== 



.. _ServerViewSet:

Server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Servers which are in communication with Calamari server, or which
have been inferred from the OSD map.  If a server is in communication
with the Calamari server then it is considered *managed*.

If a server is only known via the OSD map, then the FQDN attribute
will be set to the hostname.  This server is later added as a managed
server then the FQDN will be modified to its correct value.
    

URLs
____

============================================================================== === === ==== ===== ====== 
URL                                                                            GET PUT POST PATCH DELETE 
============================================================================== === === ==== ===== ====== 
:doc:`api/v2/server <api_example_api_v2_server>`                               Yes                       
------------------------------------------------------------------------------ --- --- ---- ----- ------ 
:doc:`api/v2/server/\<fqdn\> <api_example_api_v2_server__fqdn_>`               Yes                Yes    
------------------------------------------------------------------------------ --- --- ---- ----- ------ 
:doc:`api/v2/server/\<fqdn\>/grains <api_example_api_v2_server__fqdn__grains>` Yes                       
============================================================================== === === ==== ===== ====== 


Fields
______

============ ======== ======== ====== ====== ========================================================================================================================== 
Name         Type     Readonly Create Modify Description                                                                                                                
============ ======== ======== ====== ====== ========================================================================================================================== 
fqdn         string   False                  Fully qualified domain name                                                                                                
------------ -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
hostname     string   False                  Unqualified hostname                                                                                                       
------------ -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
managed      boolean  False                  True if this server is under Calamari server's control, falseif the server's existence was inferred via Ceph cluster maps. 
------------ -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
last_contact datetime False                  The time at which this server last communicated with the Calamariserver.  This is always null for unmanaged servers        
------------ -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
boot_time    datetime False                  The time at which this server booted. This is always null for unmanaged servers                                            
------------ -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
ceph_version string   False                  The version of Ceph installed.  This is always null for unmanaged servers.                                                 
------------ -------- -------- ------ ------ -------------------------------------------------------------------------------------------------------------------------- 
services     field    False                  List of Ceph services seenon this server                                                                                   
============ ======== ======== ====== ====== ========================================================================================================================== 



.. _SyncObject:

Sync Object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


These objects are the raw data received by the Calamari server from the Ceph cluster,
such as the cluster maps
    

URLs
____

==================================================================================================================== === === ==== ===== ====== 
URL                                                                                                                  GET PUT POST PATCH DELETE 
==================================================================================================================== === === ==== ===== ====== 
:doc:`api/v2/cluster/\<fsid\>/sync_object <api_example_api_v2_cluster__fsid__sync_object>`                           Yes                       
-------------------------------------------------------------------------------------------------------------------- --- --- ---- ----- ------ 
:doc:`api/v2/cluster/\<fsid\>/sync_object/\<sync_type\> <api_example_api_v2_cluster__fsid__sync_object__sync_type_>` Yes                       
==================================================================================================================== === === ==== ===== ====== 


Fields
______

*No field data available*


.. _UserViewSet:

User
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    The Calamari UI/API user account information.

    You may pass 'me' as the user ID to refer to the currently logged in user,
    otherwise the user ID is a numeric ID.

    Because all users are superusers, everybody can see each others accounts
    using this resource.  However, users can only modify their own account (i.e.
    the user being modified must be the user associated with the current login session).
    

URLs
____

======================================================== === === ==== ===== ====== 
URL                                                      GET PUT POST PATCH DELETE 
======================================================== === === ==== ===== ====== 
:doc:`api/v2/user <api_example_api_v2_user>`             Yes     Yes               
-------------------------------------------------------- --- --- ---- ----- ------ 
:doc:`api/v2/user/\<pk\> <api_example_api_v2_user__pk_>` Yes Yes      Yes   Yes    
======================================================== === === ==== ===== ====== 


Fields
______

======== ======= ======== ====== ====== =========================================================================== 
Name     Type    Readonly Create Modify Description                                                                 
======== ======= ======== ====== ====== =========================================================================== 
id       integer True                                                                                               
-------- ------- -------- ------ ------ --------------------------------------------------------------------------- 
username string  False                  Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters 
-------- ------- -------- ------ ------ --------------------------------------------------------------------------- 
password string  False                                                                                              
-------- ------- -------- ------ ------ --------------------------------------------------------------------------- 
email    email   False                                                                                              
======== ======= ======== ====== ====== =========================================================================== 



.. _grains:

Grains
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


The salt grains for the host running Calamari server.  These are variables
from Saltstack that tell us useful properties of the host.

The fields in this resource are passed through verbatim from SaltStack, see
the examples for which fields are available.
    

URLs
____

================================================ === === ==== ===== ====== 
URL                                              GET PUT POST PATCH DELETE 
================================================ === === ==== ===== ====== 
:doc:`api/v2/grains <api_example_api_v2_grains>` Yes                       
================================================ === === ==== ===== ====== 


Fields
______

*No field data available*


.. _login:

Login
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


This resource is used to authenticate with the REST API by POSTing a message
as follows:

::

    {
        "username": "<username>",
        "password": "<password>"
    }

If authentication is successful, 200 is returned, if it is unsuccessful
then 401 is returend.
    

URLs
____

======================================================== === === ==== ===== ====== 
URL                                                      GET PUT POST PATCH DELETE 
======================================================== === === ==== ===== ====== 
:doc:`api/v2/auth/login <api_example_api_v2_auth_login>` Yes     Yes               
======================================================== === === ==== ===== ====== 


Fields
______

*No field data available*


.. _logout:

Logout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


The resource is used to terminate an authenticated session by POSTing an
empty request.
    

URLs
____

========================================================== === === ==== ===== ====== 
URL                                                        GET PUT POST PATCH DELETE 
========================================================== === === ==== ===== ====== 
:doc:`api/v2/auth/logout <api_example_api_v2_auth_logout>` Yes     Yes               
========================================================== === === ==== ===== ====== 


Fields
______

*No field data available*


Examples
--------

.. toctree::
   :maxdepth: 1


   api_example_api_v2_cluster__fsid__crush_node

   api_example_api_v2_info

   api_example_api_v2_cluster__fsid__event

   api_example_api_v2_cluster__fsid__sync_object__sync_type_

   api_example_api_v2_cluster__fsid__mon

   api_example_api_v2_cluster__fsid__pool__pool_id_

   api_example_api_v2_request__request_id_

   api_example_api_v2_cluster__fsid__crush_node__node_id_

   api_example_api_v2_cluster__fsid__crush_rule_set

   api_example_api_v2_cluster__fsid__crush_map

   api_example_api_v2_auth_login

   api_example_api_v2_cluster__fsid__request__request_id_

   api_example_api_v2_key__minion_id_

   api_example_api_v2_cluster

   api_example_api_v2_user__pk_

   api_example_api_v2_cluster__fsid__request

   api_example_api_v2_server__fqdn__event

   api_example_api_v2_server__fqdn__grains

   api_example_api_v2_grains

   api_example_api_v2_cluster__fsid__crush_rule

   api_example_api_v2_cluster__fsid__osd _command

   api_example_api_v2_server

   api_example_api_v2_cluster__fsid__mon__mon_id_

   api_example_api_v2_cluster__fsid__log

   api_example_api_v2_cluster__fsid__sync_object

   api_example_api_v2_user

   api_example_api_v2_cluster__fsid__config

   api_example_api_v2_key

   api_example_api_v2_server__fqdn_

   api_example_api_v2_cluster__fsid__server__fqdn_

   api_example_api_v2_cluster__fsid__osd__osd_id_

   api_example_api_v2_cluster__fsid__mon__mon_id__status

   api_example_api_v2_cluster__pk_

   api_example_api_v2_server__fqdn__log__log_path_

   api_example_api_v2_cluster__fsid__server

   api_example_api_v2_event

   api_example_api_v2_cluster__fsid__pool

   api_example_api_v2_request

   api_example_api_v2_cluster__fsid__osd__osd_id__command__command_

   api_example_api_v2_cluster__fsid__osd

   api_example_api_v2_cluster__fsid__osd__osd_id__command

   api_example_api_v2_cluster__fsid__config__key_

   api_example_api_v2_server__fqdn__log

   api_example_api_v2_cluster__fsid__osd_config


