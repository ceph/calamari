Examples for api/v2/cluster/<fsid>/event
========================================

api/v2/cluster/3591a5c6-bc7d-446c-8915-95d8c08b25d7/event
---------------------------------------------------------

.. code-block:: json

   {
     "count": 4, 
     "previous": null, 
     "results": [
       {
         "message": "Started: Creating pool 'newname'", 
         "when": "2015-04-28T13:52:41.862-04:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment001.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2015-04-28T13:52:38.705-04:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment002.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2015-04-28T13:52:38.570-04:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment000.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2015-04-28T13:52:38.169-04:00", 
         "severity": "INFO"
       }
     ], 
     "next": null
   }

