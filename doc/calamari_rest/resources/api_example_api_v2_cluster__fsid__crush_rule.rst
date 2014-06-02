Examples for api/v2/cluster/<fsid>/crush_rule
=============================================

api/v2/cluster/cad0935f-e105-41db-8c71-4aa7c4602fb3/crush_rule
--------------------------------------------------------------

.. code-block:: json

   [
     {
       "name": "data", 
       "osd_count": 12, 
       "min_size": 1, 
       "steps": [
         {
           "item": -1, 
           "op": "take"
         }, 
         {
           "num": 0, 
           "type": "host", 
           "op": "chooseleaf_firstn"
         }, 
         {
           "op": "emit"
         }
       ], 
       "ruleset": 0, 
       "type": "replicated", 
       "id": 0, 
       "max_size": 10
     }, 
     {
       "name": "metadata", 
       "osd_count": 12, 
       "min_size": 1, 
       "steps": [
         {
           "item": -1, 
           "op": "take"
         }, 
         {
           "num": 0, 
           "type": "host", 
           "op": "chooseleaf_firstn"
         }, 
         {
           "op": "emit"
         }
       ], 
       "ruleset": 1, 
       "type": "replicated", 
       "id": 1, 
       "max_size": 10
     }, 
     {
       "name": "rbd", 
       "osd_count": 12, 
       "min_size": 1, 
       "steps": [
         {
           "item": -1, 
           "op": "take"
         }, 
         {
           "num": 0, 
           "type": "host", 
           "op": "chooseleaf_firstn"
         }, 
         {
           "op": "emit"
         }
       ], 
       "ruleset": 2, 
       "type": "replicated", 
       "id": 2, 
       "max_size": 10
     }
   ]

