Examples for api/v2/event
=========================

api/v2/event
------------

.. code-block:: json

   {
     "count": 58, 
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
       }, 
       {
         "message": "Calamari server started", 
         "when": "2015-04-28T13:52:16.388-04:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Started: Creating pool 'newname'", 
         "when": "2015-04-28T13:35:40.382-04:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment002.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2015-04-28T13:35:40.070-04:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment000.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2015-04-28T13:35:38.597-04:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment001.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2015-04-28T13:35:36.462-04:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Calamari server started", 
         "when": "2015-04-28T13:35:17.287-04:00", 
         "severity": "INFO"
       }
     ], 
     "next": "http://localhost:8000/api/v2/event?page=2"
   }

