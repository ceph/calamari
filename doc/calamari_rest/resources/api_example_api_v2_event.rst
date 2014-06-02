Examples for api/v2/event
=========================

api/v2/event
------------

.. code-block:: json

   {
     "count": 39, 
     "previous": null, 
     "results": [
       {
         "message": "Succeeded: Modifying pool 'data' (name=newname, id=0)", 
         "when": "2014-02-19T00:50:36.146", 
         "severity": "INFO"
       }, 
       {
         "message": "Started: Modifying pool 'data' (name=newname, id=0)", 
         "when": "2014-02-19T00:50:36.071", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment000.cluster0.com with 4 osd", 
         "when": "2014-02-19T00:50:35.182", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment001.cluster0.com with 1 mon, 4 osd", 
         "when": "2014-02-19T00:50:33.603", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment002.cluster0.com with 4 osd, 1 mon", 
         "when": "2014-02-19T00:50:33.550", 
         "severity": "INFO"
       }, 
       {
         "message": "Calamari server started", 
         "when": "2014-02-19T00:50:15.328", 
         "severity": "INFO"
       }, 
       {
         "message": "Succeeded: Modifying pool 'data' (name=newname, id=0)", 
         "when": "2014-02-19T00:49:52.807", 
         "severity": "INFO"
       }, 
       {
         "message": "Started: Modifying pool 'data' (name=newname, id=0)", 
         "when": "2014-02-19T00:49:52.731", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment000.cluster0.com with 4 osd", 
         "when": "2014-02-19T00:49:51.711", 
         "severity": "INFO"
       }, 
       {
         "message": "Added server figment002.cluster0.com with 4 osd, 1 mon", 
         "when": "2014-02-19T00:49:48.434", 
         "severity": "INFO"
       }
     ], 
     "next": "http://localhost:8000/api/v2/event?page=2"
   }

