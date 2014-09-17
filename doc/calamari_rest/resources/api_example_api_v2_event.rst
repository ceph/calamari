Examples for api/v2/event
=========================

api/v2/event
------------

.. code-block:: json

   {
     "count": 5, 
     "previous": null, 
     "results": [
       {
         "message": "Started: Creating pool 'newname'", 
         "when": "2014-09-17T19:36:43.893Z", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment000.cluster0.com with 1 monitor service, 4 OSDs", 
         "when": "2014-09-17T19:36:42.381Z", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment001.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2014-09-17T19:36:42.349Z", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment002.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2014-09-17T19:36:38.961Z", 
         "severity": "INFO"
       }, 
       {
         "message": "Calamari server started", 
         "when": "2014-09-17T19:35:55.127Z", 
         "severity": "INFO"
       }
     ], 
     "next": null
   }

