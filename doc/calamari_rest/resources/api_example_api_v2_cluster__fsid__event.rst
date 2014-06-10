Examples for api/v2/cluster/<fsid>/event
========================================

api/v2/cluster/cad0935f-e105-41db-8c71-4aa7c4602fb3/event
---------------------------------------------------------

.. code-block:: json

   {
     "count": 4, 
     "previous": null, 
     "results": [
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
       }
     ], 
     "next": null
   }

