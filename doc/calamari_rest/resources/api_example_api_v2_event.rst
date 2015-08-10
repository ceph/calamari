Examples for api/v2/event
=========================

api/v2/event
------------

.. code-block:: json

   {
     "count": 118, 
     "previous": null, 
     "results": [
       {
         "message": "Started: Creating pool 'newname'", 
         "when": "2014-11-06T13:15:15.600-08:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment002.cluster0.com with 1 monitor service, 4 OSDs", 
         "when": "2014-11-06T13:15:15.156-08:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment001.cluster0.com with 1 monitor service, 4 OSDs", 
         "when": "2014-11-06T13:15:15.116-08:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment000.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2014-11-06T13:15:05.925-08:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Calamari server started", 
         "when": "2014-11-06T13:14:21.437-08:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server vpm145.front.sepia.ceph.com with 1 OSD, 1 monitor service", 
         "when": "2014-11-06T11:33:42.431-08:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server vpm113.front.sepia.ceph.com with 1 OSD, 1 monitor service", 
         "when": "2014-11-06T11:33:38.523-08:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server vpm061.front.sepia.ceph.com with 1 OSD", 
         "when": "2014-11-06T11:33:08.764-08:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Cluster 'ceph_fake' is late reporting in", 
         "when": "2014-11-06T11:31:57.089-08:00", 
         "severity": "WARNING"
       }, 
       {
         "message": "Server figment001.cluster0.com is late reporting in, last report at 2014-11-05 08:26:44.827481-08:00", 
         "when": "2014-11-06T11:31:27.085-08:00", 
         "severity": "WARNING"
       }
     ], 
     "next": "http://localhost:8000/api/v2/event?page=2"
   }

