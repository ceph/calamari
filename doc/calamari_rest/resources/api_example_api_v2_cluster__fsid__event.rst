Examples for api/v2/cluster/<fsid>/event
========================================

api/v2/cluster/cd50fad9-74d7-4579-9acc-f0d1e4d014b4/event
---------------------------------------------------------

.. code-block:: json

   {
     "count": 4, 
     "previous": null, 
     "results": [
       {
         "message": "Started: Creating pool 'newname'", 
         "when": "2014-10-20T12:29:52.536-07:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment001.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2014-10-20T12:29:52.142-07:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment000.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2014-10-20T12:29:52.103-07:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment002.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2014-10-20T12:29:51.178-07:00", 
         "severity": "INFO"
       }
     ], 
     "next": null
   }

