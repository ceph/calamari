Examples for api/v2/cluster/<fsid>/mon/<mon_id>/status
======================================================

api/v2/cluster/cd50fad9-74d7-4579-9acc-f0d1e4d014b4/mon/figment000/status
-------------------------------------------------------------------------

.. code-block:: json

   {
     "election_epoch": 77, 
     "state": "leader", 
     "monmap": {
       "quorum": [
         0, 
         1, 
         2
       ], 
       "created": "2014-10-20T14:29:38.405317", 
       "modified": "2014-10-20T14:29:38.405311", 
       "epoch": 0, 
       "mons": [
         {
           "name": "figment000", 
           "rank": 0, 
           "addr": ""
         }, 
         {
           "name": "figment001", 
           "rank": 1, 
           "addr": ""
         }, 
         {
           "name": "figment002", 
           "rank": 2, 
           "addr": ""
         }
       ], 
       "fsid": "cd50fad9-74d7-4579-9acc-f0d1e4d014b4"
     }, 
     "rank": 0, 
     "quorum": [
       0, 
       1, 
       2
     ]
   }

