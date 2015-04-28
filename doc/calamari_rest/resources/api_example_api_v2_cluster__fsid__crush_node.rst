Examples for api/v2/cluster/<fsid>/crush_node
=============================================

api/v2/cluster/3591a5c6-bc7d-446c-8915-95d8c08b25d7/crush_node
--------------------------------------------------------------

.. code-block:: json

   [
     {
       "bucket_type": "root", 
       "hash": "rjenkins1", 
       "name": "default", 
       "weight": 4.8399505615234375, 
       "alg": "straw", 
       "items": [
         {
           "id": -2, 
           "weight": 3.0199737548828125, 
           "pos": 0
         }, 
         {
           "id": -3, 
           "weight": 0.9099884033203125, 
           "pos": 1
         }, 
         {
           "id": -4, 
           "weight": 0.9099884033203125, 
           "pos": 2
         }
       ], 
       "id": -1
     }, 
     {
       "bucket_type": "host", 
       "hash": "rjenkins1", 
       "name": "gravel1", 
       "weight": 3.0199737548828125, 
       "alg": "straw", 
       "items": [
         {
           "id": 0, 
           "weight": 0.9099884033203125, 
           "pos": 0
         }, 
         {
           "id": 3, 
           "weight": 1.8199920654296875, 
           "pos": 1
         }, 
         {
           "id": 4, 
           "weight": 0.2899932861328125, 
           "pos": 2
         }
       ], 
       "id": -2
     }, 
     {
       "bucket_type": "host", 
       "hash": "rjenkins1", 
       "name": "gravel2", 
       "weight": 0.9099884033203125, 
       "alg": "straw", 
       "items": [
         {
           "id": 1, 
           "weight": 0.9099884033203125, 
           "pos": 0
         }
       ], 
       "id": -3
     }, 
     {
       "bucket_type": "host", 
       "hash": "rjenkins1", 
       "name": "gravel3", 
       "weight": 0.9099884033203125, 
       "alg": "straw", 
       "items": [
         {
           "id": 2, 
           "weight": 0.9099884033203125, 
           "pos": 0
         }
       ], 
       "id": -4
     }
   ]

