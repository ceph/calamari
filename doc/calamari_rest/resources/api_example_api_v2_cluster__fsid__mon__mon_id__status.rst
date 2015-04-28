Examples for api/v2/cluster/<fsid>/mon/<mon_id>/status
======================================================

api/v2/cluster/3591a5c6-bc7d-446c-8915-95d8c08b25d7/mon/figment000/status
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
       "created": "2015-04-28T12:52:18.364360", 
       "modified": "2015-04-28T12:52:18.364353", 
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
       "fsid": "3591a5c6-bc7d-446c-8915-95d8c08b25d7"
     }, 
     "rank": 0, 
     "quorum": [
       0, 
       1, 
       2
     ]
   }

