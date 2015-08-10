Examples for api/v2/server/<fqdn>
=================================

api/v2/server/figment000.cluster0.com
-------------------------------------

.. code-block:: json

   {
     "managed": true, 
     "last_contact": "2014-11-06T21:15:15.156841+00:00", 
     "hostname": "figment000", 
     "fqdn": "figment000.cluster0.com", 
     "boot_time": "1970-01-02T10:17:36+00:00", 
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
     "ceph_version": "0.67.8-simulator"
   }

