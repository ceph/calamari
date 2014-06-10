Examples for api/v2/cluster/<fsid>/server/<fqdn>
================================================

api/v2/cluster/cad0935f-e105-41db-8c71-4aa7c4602fb3/server/figment000.cluster0.com
----------------------------------------------------------------------------------

.. code-block:: json

   {
     "managed": true, 
     "last_contact": "2014-02-19T00:50:35.182615+00:00", 
     "backend_addr": "", 
     "hostname": "figment000", 
     "frontend_iface": null, 
     "fqdn": "figment000.cluster0.com", 
     "frontend_addr": "", 
     "services": [
       {
         "running": true, 
         "type": "osd", 
         "id": "2", 
         "fsid": "cad0935f-e105-41db-8c71-4aa7c4602fb3"
       }, 
       {
         "running": true, 
         "type": "osd", 
         "id": "1", 
         "fsid": "cad0935f-e105-41db-8c71-4aa7c4602fb3"
       }, 
       {
         "running": true, 
         "type": "osd", 
         "id": "0", 
         "fsid": "cad0935f-e105-41db-8c71-4aa7c4602fb3"
       }, 
       {
         "running": true, 
         "type": "mon", 
         "id": "figment000", 
         "fsid": "cad0935f-e105-41db-8c71-4aa7c4602fb3"
       }, 
       {
         "running": true, 
         "type": "osd", 
         "id": "3", 
         "fsid": "cad0935f-e105-41db-8c71-4aa7c4602fb3"
       }
     ], 
     "backend_iface": null
   }

