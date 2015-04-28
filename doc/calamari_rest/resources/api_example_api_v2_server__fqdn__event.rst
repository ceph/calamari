Examples for api/v2/server/<fqdn>/event
=======================================

api/v2/server/figment000.cluster0.com/event
-------------------------------------------

.. code-block:: json

   {
     "count": 11, 
     "previous": null, 
     "results": [
       {
         "message": "Added server figment000.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2015-04-28T13:52:38.169-04:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment000.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2015-04-28T13:35:38.597-04:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment000.cluster0.com with 1 monitor service, 4 OSDs", 
         "when": "2015-04-28T13:34:29.585-04:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment000.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2015-04-28T13:31:44.144-04:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment000.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2015-04-28T13:26:57.139-04:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment000.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2015-04-28T11:50:00.303-04:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Server figment000.cluster0.com is late reporting in, last report at 2015-04-28 11:33:32.079281-04:00", 
         "when": "2015-04-28T11:36:13.233-04:00", 
         "severity": "WARNING"
       }, 
       {
         "message": "Added server figment000.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2015-04-28T11:33:32.080-04:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment000.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2015-04-27T12:26:39.593-04:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment000.cluster0.com with 1 monitor service, 4 OSDs", 
         "when": "2015-04-27T11:48:36.058-04:00", 
         "severity": "INFO"
       }
     ], 
     "next": "http://localhost:8000/api/v2/server/figment000.cluster0.com/event?page=2"
   }

