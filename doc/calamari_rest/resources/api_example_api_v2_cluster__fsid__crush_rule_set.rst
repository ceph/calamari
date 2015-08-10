Examples for api/v2/cluster/<fsid>/crush_rule_set
=================================================

api/v2/cluster/dce20d46-f010-4883-988c-4a6d8bd15793/crush_rule_set
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

