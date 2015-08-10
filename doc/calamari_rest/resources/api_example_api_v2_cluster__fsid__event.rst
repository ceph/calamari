Examples for api/v2/cluster/<fsid>/event
========================================

api/v2/cluster/dce20d46-f010-4883-988c-4a6d8bd15793/event
---------------------------------------------------------

.. code-block:: json

   {
     "count": 4, 
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
       }
     ], 
     "next": null
   }

