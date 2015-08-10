Examples for api/v2/cluster/<fsid>/mon/<mon_id>/status
======================================================

api/v2/cluster/dce20d46-f010-4883-988c-4a6d8bd15793/mon/figment000/status
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
       "created": "2014-11-06T15:14:34.316557", 
       "modified": "2014-11-06T15:14:34.316541", 
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
       "fsid": "dce20d46-f010-4883-988c-4a6d8bd15793"
     }, 
     "rank": 0, 
     "quorum": [
       0, 
       1, 
       2
     ]
   }

