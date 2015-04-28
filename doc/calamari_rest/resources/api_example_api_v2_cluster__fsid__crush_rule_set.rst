Examples for api/v2/cluster/<fsid>/crush_rule_set
=================================================

api/v2/cluster/3591a5c6-bc7d-446c-8915-95d8c08b25d7/crush_rule_set
------------------------------------------------------------------

.. code-block:: json

   [
     {
       "rules": [
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
         }
       ], 
       "id": 0
     }, 
     {
       "rules": [
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
         }
       ], 
       "id": 1
     }, 
     {
       "rules": [
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
       ], 
       "id": 2
     }
   ]

