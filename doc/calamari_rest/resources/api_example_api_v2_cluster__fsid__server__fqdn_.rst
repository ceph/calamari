Examples for api/v2/cluster/<fsid>/server/<fqdn>
================================================

api/v2/cluster/dce20d46-f010-4883-988c-4a6d8bd15793/server/figment000.cluster0.com
----------------------------------------------------------------------------------

.. code-block:: json

   {
     "managed": true, 
     "last_contact": "2014-11-06T21:15:15.156841+00:00", 
     "ceph_version": "0.67.8-simulator", 
     "backend_addr": "", 
     "hostname": "figment000", 
     "frontend_iface": null, 
     "fqdn": "figment000.cluster0.com", 
     "boot_time": "1970-01-02T10:17:36+00:00", 
     "frontend_addr": "", 
     "services": [
       {
         "running": true, 
         "type": "osd", 
         "id": "3", 
         "fsid": "dce20d46-f010-4883-988c-4a6d8bd15793"
       }, 
       {
         "running": true, 
         "type": "osd", 
         "id": "0", 
         "fsid": "dce20d46-f010-4883-988c-4a6d8bd15793"
       }, 
       {
         "running": true, 
         "type": "mon", 
         "id": "figment000", 
         "fsid": "dce20d46-f010-4883-988c-4a6d8bd15793"
       }, 
       {
         "running": true, 
         "type": "osd", 
         "id": "1", 
         "fsid": "dce20d46-f010-4883-988c-4a6d8bd15793"
       }, 
       {
         "running": true, 
         "type": "osd", 
         "id": "2", 
         "fsid": "dce20d46-f010-4883-988c-4a6d8bd15793"
       }
     ], 
     "backend_iface": null
   }

