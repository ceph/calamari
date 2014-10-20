Examples for api/v2/event
=========================

api/v2/event
------------

.. code-block:: json

   {
     "count": 113, 
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
       }, 
       {
         "message": "Calamari server started", 
         "when": "2014-10-20T12:29:35.286-07:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Started: Creating pool 'newname'", 
         "when": "2014-10-20T12:27:10.859-07:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment001.cluster0.com with 1 monitor service, 4 OSDs", 
         "when": "2014-10-20T12:27:09.994-07:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment002.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2014-10-20T12:27:09.469-07:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment000.cluster0.com with 4 OSDs, 1 monitor service", 
         "when": "2014-10-20T12:27:08.631-07:00", 
         "severity": "INFO"
       }, 
       {
         "message": "Calamari server started", 
         "when": "2014-10-20T12:26:52.246-07:00", 
         "severity": "INFO"
       }
     ], 
     "next": "http://localhost:8000/api/v2/event?page=2"
   }

