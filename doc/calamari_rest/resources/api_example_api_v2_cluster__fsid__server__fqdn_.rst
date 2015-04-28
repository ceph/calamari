Examples for api/v2/cluster/<fsid>/server/<fqdn>
================================================

api/v2/cluster/3591a5c6-bc7d-446c-8915-95d8c08b25d7/server/figment000.cluster0.com
----------------------------------------------------------------------------------

.. code-block:: json

   {
     "managed": true, 
     "last_contact": "2015-04-28T17:52:38.168016+00:00", 
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
         "id": "1", 
         "fsid": "3591a5c6-bc7d-446c-8915-95d8c08b25d7"
       }, 
       {
         "running": true, 
         "type": "osd", 
         "id": "0", 
         "fsid": "3591a5c6-bc7d-446c-8915-95d8c08b25d7"
       }, 
       {
         "running": true, 
         "type": "mon", 
         "id": "figment000", 
         "fsid": "3591a5c6-bc7d-446c-8915-95d8c08b25d7"
       }, 
       {
         "running": true, 
         "type": "osd", 
         "id": "2", 
         "fsid": "3591a5c6-bc7d-446c-8915-95d8c08b25d7"
       }, 
       {
         "running": true, 
         "type": "osd", 
         "id": "3", 
         "fsid": "3591a5c6-bc7d-446c-8915-95d8c08b25d7"
       }
     ], 
     "backend_iface": null
   }

