Examples for api/v2/server/<fqdn>/event
=======================================

api/v2/server/figment000.cluster0.com/event
-------------------------------------------

.. code-block:: json

   {
     "count": 9, 
     "previous": null, 
     "results": [
       {
         "message": "Added server figment000.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2014-11-06T13:15:05.925-08:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Server figment000.cluster0.com is late reporting in, last report at 2014-11-05 08:26:42.660646-08:00", 
         "when": "2014-11-06T11:31:27.050-08:00", 
         "severity": "WARNING"
       }, 
       {
         "message": "Added server figment000.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2014-11-05T08:26:42.662-08:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Server figment000.cluster0.com regained contact", 
         "when": "2014-11-05T08:11:29.101-08:00", 
         "severity": "RECOVERY"
       }, 
       {
         "message": "Added server figment000.cluster0.com with 1 monitor service, 4 OSDs", 
         "when": "2014-11-05T08:11:19.136-08:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Server figment000.cluster0.com is late reporting in, last report at 2014-11-05 06:30:14.288472-08:00", 
         "when": "2014-11-05T08:10:57.853-08:00", 
         "severity": "WARNING"
       }, 
       {
         "message": "Server figment000.cluster0.com is late reporting in, last report at 2014-11-05 06:30:14.288472-08:00", 
         "when": "2014-11-05T06:32:56.452-08:00", 
         "severity": "WARNING"
       }, 
       {
         "message": "Added server figment000.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2014-11-05T06:30:14.289-08:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment000.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2014-11-05T06:27:40.891-08:00", 
         "severity": "INFO"
       }
     ], 
     "next": null
   }

