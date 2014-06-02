Examples for api/v2/cluster/<fsid>/derived_object/<derived_type>
================================================================

api/v2/cluster/cad0935f-e105-41db-8c71-4aa7c4602fb3/derived_object/osds_by_pg_state
-----------------------------------------------------------------------------------

.. code-block:: json

   {
     "active": [
       0, 
       1, 
       2, 
       3, 
       4, 
       5, 
       6, 
       7, 
       8, 
       9, 
       10, 
       11
     ], 
     "clean": [
       0, 
       1, 
       2, 
       3, 
       4, 
       5, 
       6, 
       7, 
       8, 
       9, 
       10, 
       11
     ]
   }

api/v2/cluster/cad0935f-e105-41db-8c71-4aa7c4602fb3/derived_object/osds
-----------------------------------------------------------------------

.. code-block:: json

   [
     {
       "uuid": "71ec6efb-3208-4c00-8a94-dccc068b51a5", 
       "heartbeat_front_addr": "", 
       "heartbeat_back_addr": "", 
       "osd": 0, 
       "fqdn": "figment000", 
       "up": 1, 
       "up_from": 0, 
       "host": "figment000", 
       "in": 1, 
       "pools": [
         "rbd", 
         "data", 
         "metadata"
       ], 
       "pg_states": {
         "active": 24, 
         "clean": 24
       }, 
       "cluster_addr": "", 
       "id": 0, 
       "public_addr": ""
     }, 
     {
       "uuid": "7c2bf7f0-125c-407d-b00e-7f2d197274a0", 
       "heartbeat_front_addr": "", 
       "heartbeat_back_addr": "", 
       "osd": 1, 
       "fqdn": "figment000", 
       "up": 1, 
       "up_from": 0, 
       "host": "figment000", 
       "in": 1, 
       "pools": [
         "rbd", 
         "data", 
         "metadata"
       ], 
       "pg_states": {
         "active": 24, 
         "clean": 24
       }, 
       "cluster_addr": "", 
       "id": 1, 
       "public_addr": ""
     }, 
     {
       "uuid": "f459eb16-93e6-473b-97d5-55b584cb8f9c", 
       "heartbeat_front_addr": "", 
       "heartbeat_back_addr": "", 
       "osd": 2, 
       "fqdn": "figment000", 
       "up": 1, 
       "up_from": 0, 
       "host": "figment000", 
       "in": 1, 
       "pools": [
         "rbd", 
         "data", 
         "metadata"
       ], 
       "pg_states": {
         "active": 35, 
         "clean": 35
       }, 
       "cluster_addr": "", 
       "id": 2, 
       "public_addr": ""
     }, 
     {
       "uuid": "7c2cee1e-c1c1-41d4-bff1-8fc8bba9f4e4", 
       "heartbeat_front_addr": "", 
       "heartbeat_back_addr": "", 
       "osd": 3, 
       "fqdn": "figment000", 
       "up": 1, 
       "up_from": 0, 
       "host": "figment000", 
       "in": 1, 
       "pools": [
         "rbd", 
         "data", 
         "metadata"
       ], 
       "pg_states": {
         "active": 35, 
         "clean": 35
       }, 
       "cluster_addr": "", 
       "id": 3, 
       "public_addr": ""
     }, 
     {
       "uuid": "14f75388-b21c-4e95-96aa-d95de00d7525", 
       "heartbeat_front_addr": "", 
       "heartbeat_back_addr": "", 
       "osd": 4, 
       "fqdn": "figment001.cluster0.com", 
       "up": 1, 
       "up_from": 0, 
       "host": "figment001", 
       "in": 1, 
       "pools": [
         "rbd", 
         "data", 
         "metadata"
       ], 
       "pg_states": {
         "active": 35, 
         "clean": 35
       }, 
       "cluster_addr": "", 
       "id": 4, 
       "public_addr": ""
     }, 
     {
       "uuid": "ddc12406-4e0a-4c52-b631-bdbb9a289321", 
       "heartbeat_front_addr": "", 
       "heartbeat_back_addr": "", 
       "osd": 5, 
       "fqdn": "figment001.cluster0.com", 
       "up": 1, 
       "up_from": 0, 
       "host": "figment001", 
       "in": 1, 
       "pools": [
         "rbd", 
         "data", 
         "metadata"
       ], 
       "pg_states": {
         "active": 35, 
         "clean": 35
       }, 
       "cluster_addr": "", 
       "id": 5, 
       "public_addr": ""
     }, 
     {
       "uuid": "5a7082be-e52a-406e-a718-d3a347ff8c7b", 
       "heartbeat_front_addr": "", 
       "heartbeat_back_addr": "", 
       "osd": 6, 
       "fqdn": "figment001.cluster0.com", 
       "up": 1, 
       "up_from": 0, 
       "host": "figment001", 
       "in": 1, 
       "pools": [
         "rbd", 
         "data", 
         "metadata"
       ], 
       "pg_states": {
         "active": 33, 
         "clean": 33
       }, 
       "cluster_addr": "", 
       "id": 6, 
       "public_addr": ""
     }, 
     {
       "uuid": "e6aea034-934b-4e4d-900c-a5d2e6f89214", 
       "heartbeat_front_addr": "", 
       "heartbeat_back_addr": "", 
       "osd": 7, 
       "fqdn": "figment001.cluster0.com", 
       "up": 1, 
       "up_from": 0, 
       "host": "figment001", 
       "in": 1, 
       "pools": [
         "rbd", 
         "data", 
         "metadata"
       ], 
       "pg_states": {
         "active": 33, 
         "clean": 33
       }, 
       "cluster_addr": "", 
       "id": 7, 
       "public_addr": ""
     }, 
     {
       "uuid": "93d86b22-8e99-41e5-92a5-f85d983c2918", 
       "heartbeat_front_addr": "", 
       "heartbeat_back_addr": "", 
       "osd": 8, 
       "fqdn": "figment002.cluster0.com", 
       "up": 1, 
       "up_from": 0, 
       "host": "figment002", 
       "in": 1, 
       "pools": [
         "rbd", 
         "data", 
         "metadata"
       ], 
       "pg_states": {
         "active": 37, 
         "clean": 37
       }, 
       "cluster_addr": "", 
       "id": 8, 
       "public_addr": ""
     }, 
     {
       "uuid": "46df62ad-6fda-4a07-b4a7-80310468e1b1", 
       "heartbeat_front_addr": "", 
       "heartbeat_back_addr": "", 
       "osd": 9, 
       "fqdn": "figment002.cluster0.com", 
       "up": 1, 
       "up_from": 0, 
       "host": "figment002", 
       "in": 1, 
       "pools": [
         "rbd", 
         "data", 
         "metadata"
       ], 
       "pg_states": {
         "active": 37, 
         "clean": 37
       }, 
       "cluster_addr": "", 
       "id": 9, 
       "public_addr": ""
     }, 
     {
       "uuid": "2d7eb7b5-91d3-40aa-8068-67417ee93542", 
       "heartbeat_front_addr": "", 
       "heartbeat_back_addr": "", 
       "osd": 10, 
       "fqdn": "figment002.cluster0.com", 
       "up": 1, 
       "up_from": 0, 
       "host": "figment002", 
       "in": 1, 
       "pools": [
         "rbd", 
         "data", 
         "metadata"
       ], 
       "pg_states": {
         "active": 28, 
         "clean": 28
       }, 
       "cluster_addr": "", 
       "id": 10, 
       "public_addr": ""
     }, 
     {
       "uuid": "22599ab7-505b-4ae2-8da0-2b1bfdb8ca8b", 
       "heartbeat_front_addr": "", 
       "heartbeat_back_addr": "", 
       "osd": 11, 
       "fqdn": "figment002.cluster0.com", 
       "up": 1, 
       "up_from": 0, 
       "host": "figment002", 
       "in": 1, 
       "pools": [
         "rbd", 
         "data", 
         "metadata"
       ], 
       "pg_states": {
         "active": 28, 
         "clean": 28
       }, 
       "cluster_addr": "", 
       "id": 11, 
       "public_addr": ""
     }
   ]

api/v2/cluster/cad0935f-e105-41db-8c71-4aa7c4602fb3/derived_object/pgs
----------------------------------------------------------------------

.. code-block:: json

   [
     {
       "acting": [
         2, 
         3
       ], 
       "pgid": "0.0", 
       "up": [
         2, 
         3
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         9, 
         8
       ], 
       "pgid": "0.1", 
       "up": [
         9, 
         8
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         8, 
         9
       ], 
       "pgid": "0.2", 
       "up": [
         8, 
         9
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         3, 
         2
       ], 
       "pgid": "0.3", 
       "up": [
         3, 
         2
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         6, 
         7
       ], 
       "pgid": "0.4", 
       "up": [
         6, 
         7
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         5, 
         4
       ], 
       "pgid": "0.5", 
       "up": [
         5, 
         4
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         8, 
         9
       ], 
       "pgid": "0.6", 
       "up": [
         8, 
         9
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         3, 
         2
       ], 
       "pgid": "0.7", 
       "up": [
         3, 
         2
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         2, 
         3
       ], 
       "pgid": "0.8", 
       "up": [
         2, 
         3
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         5, 
         4
       ], 
       "pgid": "0.9", 
       "up": [
         5, 
         4
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         2, 
         3
       ], 
       "pgid": "0.10", 
       "up": [
         2, 
         3
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         9, 
         8
       ], 
       "pgid": "0.11", 
       "up": [
         9, 
         8
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         4, 
         5
       ], 
       "pgid": "0.12", 
       "up": [
         4, 
         5
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         3, 
         2
       ], 
       "pgid": "0.13", 
       "up": [
         3, 
         2
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         10, 
         11
       ], 
       "pgid": "0.14", 
       "up": [
         10, 
         11
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         5, 
         4
       ], 
       "pgid": "0.15", 
       "up": [
         5, 
         4
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         0, 
         1
       ], 
       "pgid": "0.16", 
       "up": [
         0, 
         1
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         3, 
         2
       ], 
       "pgid": "0.17", 
       "up": [
         3, 
         2
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         10, 
         11
       ], 
       "pgid": "0.18", 
       "up": [
         10, 
         11
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         5, 
         4
       ], 
       "pgid": "0.19", 
       "up": [
         5, 
         4
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         9, 
         8
       ], 
       "pgid": "0.20", 
       "up": [
         9, 
         8
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         2, 
         3
       ], 
       "pgid": "0.21", 
       "up": [
         2, 
         3
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         3, 
         2
       ], 
       "pgid": "0.22", 
       "up": [
         3, 
         2
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         4, 
         5
       ], 
       "pgid": "0.23", 
       "up": [
         4, 
         5
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         5, 
         4
       ], 
       "pgid": "0.24", 
       "up": [
         5, 
         4
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         10, 
         11
       ], 
       "pgid": "0.25", 
       "up": [
         10, 
         11
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         3, 
         2
       ], 
       "pgid": "0.26", 
       "up": [
         3, 
         2
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         0, 
         1
       ], 
       "pgid": "0.27", 
       "up": [
         0, 
         1
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         9, 
         8
       ], 
       "pgid": "0.28", 
       "up": [
         9, 
         8
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         2, 
         3
       ], 
       "pgid": "0.29", 
       "up": [
         2, 
         3
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         8, 
         9
       ], 
       "pgid": "0.30", 
       "up": [
         8, 
         9
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         7, 
         6
       ], 
       "pgid": "0.31", 
       "up": [
         7, 
         6
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         6, 
         7
       ], 
       "pgid": "0.32", 
       "up": [
         6, 
         7
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         1, 
         0
       ], 
       "pgid": "0.33", 
       "up": [
         1, 
         0
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         4, 
         5
       ], 
       "pgid": "0.34", 
       "up": [
         4, 
         5
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         7, 
         6
       ], 
       "pgid": "0.35", 
       "up": [
         7, 
         6
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         2, 
         3
       ], 
       "pgid": "0.36", 
       "up": [
         2, 
         3
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         9, 
         8
       ], 
       "pgid": "0.37", 
       "up": [
         9, 
         8
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         8, 
         9
       ], 
       "pgid": "0.38", 
       "up": [
         8, 
         9
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         7, 
         6
       ], 
       "pgid": "0.39", 
       "up": [
         7, 
         6
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         11, 
         10
       ], 
       "pgid": "0.40", 
       "up": [
         11, 
         10
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         4, 
         5
       ], 
       "pgid": "0.41", 
       "up": [
         4, 
         5
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         5, 
         4
       ], 
       "pgid": "0.42", 
       "up": [
         5, 
         4
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         10, 
         11
       ], 
       "pgid": "0.43", 
       "up": [
         10, 
         11
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         3, 
         2
       ], 
       "pgid": "0.44", 
       "up": [
         3, 
         2
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         0, 
         1
       ], 
       "pgid": "0.45", 
       "up": [
         0, 
         1
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         5, 
         4
       ], 
       "pgid": "0.46", 
       "up": [
         5, 
         4
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         10, 
         11
       ], 
       "pgid": "0.47", 
       "up": [
         10, 
         11
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         3, 
         2
       ], 
       "pgid": "0.48", 
       "up": [
         3, 
         2
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         4, 
         5
       ], 
       "pgid": "0.49", 
       "up": [
         4, 
         5
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         2, 
         3
       ], 
       "pgid": "0.50", 
       "up": [
         2, 
         3
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         9, 
         8
       ], 
       "pgid": "0.51", 
       "up": [
         9, 
         8
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         4, 
         5
       ], 
       "pgid": "0.52", 
       "up": [
         4, 
         5
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         7, 
         6
       ], 
       "pgid": "0.53", 
       "up": [
         7, 
         6
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         2, 
         3
       ], 
       "pgid": "0.54", 
       "up": [
         2, 
         3
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         9, 
         8
       ], 
       "pgid": "0.55", 
       "up": [
         9, 
         8
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         8, 
         9
       ], 
       "pgid": "0.56", 
       "up": [
         8, 
         9
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         3, 
         2
       ], 
       "pgid": "0.57", 
       "up": [
         3, 
         2
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         2, 
         3
       ], 
       "pgid": "0.58", 
       "up": [
         2, 
         3
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         9, 
         8
       ], 
       "pgid": "0.59", 
       "up": [
         9, 
         8
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         9, 
         8
       ], 
       "pgid": "0.60", 
       "up": [
         9, 
         8
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         2, 
         3
       ], 
       "pgid": "0.61", 
       "up": [
         2, 
         3
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         7, 
         6
       ], 
       "pgid": "0.62", 
       "up": [
         7, 
         6
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         4, 
         5
       ], 
       "pgid": "0.63", 
       "up": [
         4, 
         5
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         9, 
         8
       ], 
       "pgid": "1.0", 
       "up": [
         9, 
         8
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         10, 
         11
       ], 
       "pgid": "1.1", 
       "up": [
         10, 
         11
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         3, 
         2
       ], 
       "pgid": "1.2", 
       "up": [
         3, 
         2
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         8, 
         9
       ], 
       "pgid": "1.3", 
       "up": [
         8, 
         9
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         9, 
         8
       ], 
       "pgid": "1.4", 
       "up": [
         9, 
         8
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         6, 
         7
       ], 
       "pgid": "1.5", 
       "up": [
         6, 
         7
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         7, 
         6
       ], 
       "pgid": "1.6", 
       "up": [
         7, 
         6
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         0, 
         1
       ], 
       "pgid": "1.7", 
       "up": [
         0, 
         1
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         9, 
         8
       ], 
       "pgid": "1.8", 
       "up": [
         9, 
         8
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         10, 
         11
       ], 
       "pgid": "1.9", 
       "up": [
         10, 
         11
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         7, 
         6
       ], 
       "pgid": "1.10", 
       "up": [
         7, 
         6
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         8, 
         9
       ], 
       "pgid": "1.11", 
       "up": [
         8, 
         9
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         1, 
         0
       ], 
       "pgid": "1.12", 
       "up": [
         1, 
         0
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         6, 
         7
       ], 
       "pgid": "1.13", 
       "up": [
         6, 
         7
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         11, 
         10
       ], 
       "pgid": "1.14", 
       "up": [
         11, 
         10
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         8, 
         9
       ], 
       "pgid": "1.15", 
       "up": [
         8, 
         9
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         9, 
         8
       ], 
       "pgid": "1.16", 
       "up": [
         9, 
         8
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         2, 
         3
       ], 
       "pgid": "1.17", 
       "up": [
         2, 
         3
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         7, 
         6
       ], 
       "pgid": "1.18", 
       "up": [
         7, 
         6
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         8, 
         9
       ], 
       "pgid": "1.19", 
       "up": [
         8, 
         9
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         4, 
         5
       ], 
       "pgid": "1.20", 
       "up": [
         4, 
         5
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         7, 
         6
       ], 
       "pgid": "1.21", 
       "up": [
         7, 
         6
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         2, 
         3
       ], 
       "pgid": "1.22", 
       "up": [
         2, 
         3
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         9, 
         8
       ], 
       "pgid": "1.23", 
       "up": [
         9, 
         8
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         8, 
         9
       ], 
       "pgid": "1.24", 
       "up": [
         8, 
         9
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         3, 
         2
       ], 
       "pgid": "1.25", 
       "up": [
         3, 
         2
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         2, 
         3
       ], 
       "pgid": "1.26", 
       "up": [
         2, 
         3
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         9, 
         8
       ], 
       "pgid": "1.27", 
       "up": [
         9, 
         8
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         4, 
         5
       ], 
       "pgid": "1.28", 
       "up": [
         4, 
         5
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         7, 
         6
       ], 
       "pgid": "1.29", 
       "up": [
         7, 
         6
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         5, 
         4
       ], 
       "pgid": "1.30", 
       "up": [
         5, 
         4
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         10, 
         11
       ], 
       "pgid": "1.31", 
       "up": [
         10, 
         11
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         3, 
         2
       ], 
       "pgid": "1.32", 
       "up": [
         3, 
         2
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         0, 
         1
       ], 
       "pgid": "1.33", 
       "up": [
         0, 
         1
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         5, 
         4
       ], 
       "pgid": "1.34", 
       "up": [
         5, 
         4
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         10, 
         11
       ], 
       "pgid": "1.35", 
       "up": [
         10, 
         11
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         11, 
         10
       ], 
       "pgid": "1.36", 
       "up": [
         11, 
         10
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         4, 
         5
       ], 
       "pgid": "1.37", 
       "up": [
         4, 
         5
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         1, 
         0
       ], 
       "pgid": "1.38", 
       "up": [
         1, 
         0
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         6, 
         7
       ], 
       "pgid": "1.39", 
       "up": [
         6, 
         7
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         6, 
         7
       ], 
       "pgid": "1.40", 
       "up": [
         6, 
         7
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         1, 
         0
       ], 
       "pgid": "1.41", 
       "up": [
         1, 
         0
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         0, 
         1
       ], 
       "pgid": "1.42", 
       "up": [
         0, 
         1
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         7, 
         6
       ], 
       "pgid": "1.43", 
       "up": [
         7, 
         6
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         6, 
         7
       ], 
       "pgid": "1.44", 
       "up": [
         6, 
         7
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         1, 
         0
       ], 
       "pgid": "1.45", 
       "up": [
         1, 
         0
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         8, 
         9
       ], 
       "pgid": "1.46", 
       "up": [
         8, 
         9
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         11, 
         10
       ], 
       "pgid": "1.47", 
       "up": [
         11, 
         10
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         6, 
         7
       ], 
       "pgid": "1.48", 
       "up": [
         6, 
         7
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         1, 
         0
       ], 
       "pgid": "1.49", 
       "up": [
         1, 
         0
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         7, 
         6
       ], 
       "pgid": "1.50", 
       "up": [
         7, 
         6
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         4, 
         5
       ], 
       "pgid": "1.51", 
       "up": [
         4, 
         5
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         5, 
         4
       ], 
       "pgid": "1.52", 
       "up": [
         5, 
         4
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         10, 
         11
       ], 
       "pgid": "1.53", 
       "up": [
         10, 
         11
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         3, 
         2
       ], 
       "pgid": "1.54", 
       "up": [
         3, 
         2
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         4, 
         5
       ], 
       "pgid": "1.55", 
       "up": [
         4, 
         5
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         9, 
         8
       ], 
       "pgid": "1.56", 
       "up": [
         9, 
         8
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         2, 
         3
       ], 
       "pgid": "1.57", 
       "up": [
         2, 
         3
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         7, 
         6
       ], 
       "pgid": "1.58", 
       "up": [
         7, 
         6
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         4, 
         5
       ], 
       "pgid": "1.59", 
       "up": [
         4, 
         5
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         0, 
         1
       ], 
       "pgid": "1.60", 
       "up": [
         0, 
         1
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         11, 
         10
       ], 
       "pgid": "1.61", 
       "up": [
         11, 
         10
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         10, 
         11
       ], 
       "pgid": "1.62", 
       "up": [
         10, 
         11
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         5, 
         4
       ], 
       "pgid": "1.63", 
       "up": [
         5, 
         4
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         0, 
         1
       ], 
       "pgid": "2.0", 
       "up": [
         0, 
         1
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         7, 
         6
       ], 
       "pgid": "2.1", 
       "up": [
         7, 
         6
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         6, 
         7
       ], 
       "pgid": "2.2", 
       "up": [
         6, 
         7
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         1, 
         0
       ], 
       "pgid": "2.3", 
       "up": [
         1, 
         0
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         0, 
         1
       ], 
       "pgid": "2.4", 
       "up": [
         0, 
         1
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         7, 
         6
       ], 
       "pgid": "2.5", 
       "up": [
         7, 
         6
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         10, 
         11
       ], 
       "pgid": "2.6", 
       "up": [
         10, 
         11
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         9, 
         8
       ], 
       "pgid": "2.7", 
       "up": [
         9, 
         8
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         4, 
         5
       ], 
       "pgid": "2.8", 
       "up": [
         4, 
         5
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         11, 
         10
       ], 
       "pgid": "2.9", 
       "up": [
         11, 
         10
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         8, 
         9
       ], 
       "pgid": "2.10", 
       "up": [
         8, 
         9
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         3, 
         2
       ], 
       "pgid": "2.11", 
       "up": [
         3, 
         2
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         2, 
         3
       ], 
       "pgid": "2.12", 
       "up": [
         2, 
         3
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         9, 
         8
       ], 
       "pgid": "2.13", 
       "up": [
         9, 
         8
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         4, 
         5
       ], 
       "pgid": "2.14", 
       "up": [
         4, 
         5
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         7, 
         6
       ], 
       "pgid": "2.15", 
       "up": [
         7, 
         6
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         2, 
         3
       ], 
       "pgid": "2.16", 
       "up": [
         2, 
         3
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         9, 
         8
       ], 
       "pgid": "2.17", 
       "up": [
         9, 
         8
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         4, 
         5
       ], 
       "pgid": "2.18", 
       "up": [
         4, 
         5
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         3, 
         2
       ], 
       "pgid": "2.19", 
       "up": [
         3, 
         2
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         11, 
         10
       ], 
       "pgid": "2.20", 
       "up": [
         11, 
         10
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         8, 
         9
       ], 
       "pgid": "2.21", 
       "up": [
         8, 
         9
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         1, 
         0
       ], 
       "pgid": "2.22", 
       "up": [
         1, 
         0
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         6, 
         7
       ], 
       "pgid": "2.23", 
       "up": [
         6, 
         7
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         7, 
         6
       ], 
       "pgid": "2.24", 
       "up": [
         7, 
         6
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         0, 
         1
       ], 
       "pgid": "2.25", 
       "up": [
         0, 
         1
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         1, 
         0
       ], 
       "pgid": "2.26", 
       "up": [
         1, 
         0
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         6, 
         7
       ], 
       "pgid": "2.27", 
       "up": [
         6, 
         7
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         11, 
         10
       ], 
       "pgid": "2.28", 
       "up": [
         11, 
         10
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         8, 
         9
       ], 
       "pgid": "2.29", 
       "up": [
         8, 
         9
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         10, 
         11
       ], 
       "pgid": "2.30", 
       "up": [
         10, 
         11
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         5, 
         4
       ], 
       "pgid": "2.31", 
       "up": [
         5, 
         4
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         0, 
         1
       ], 
       "pgid": "2.32", 
       "up": [
         0, 
         1
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         11, 
         10
       ], 
       "pgid": "2.33", 
       "up": [
         11, 
         10
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         6, 
         7
       ], 
       "pgid": "2.34", 
       "up": [
         6, 
         7
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         1, 
         0
       ], 
       "pgid": "2.35", 
       "up": [
         1, 
         0
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         0, 
         1
       ], 
       "pgid": "2.36", 
       "up": [
         0, 
         1
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         3, 
         2
       ], 
       "pgid": "2.37", 
       "up": [
         3, 
         2
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         10, 
         11
       ], 
       "pgid": "2.38", 
       "up": [
         10, 
         11
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         5, 
         4
       ], 
       "pgid": "2.39", 
       "up": [
         5, 
         4
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         5, 
         4
       ], 
       "pgid": "2.40", 
       "up": [
         5, 
         4
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         10, 
         11
       ], 
       "pgid": "2.41", 
       "up": [
         10, 
         11
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         7, 
         6
       ], 
       "pgid": "2.42", 
       "up": [
         7, 
         6
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         4, 
         5
       ], 
       "pgid": "2.43", 
       "up": [
         4, 
         5
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         9, 
         8
       ], 
       "pgid": "2.44", 
       "up": [
         9, 
         8
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         2, 
         3
       ], 
       "pgid": "2.45", 
       "up": [
         2, 
         3
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         3, 
         2
       ], 
       "pgid": "2.46", 
       "up": [
         3, 
         2
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         4, 
         5
       ], 
       "pgid": "2.47", 
       "up": [
         4, 
         5
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         5, 
         4
       ], 
       "pgid": "2.48", 
       "up": [
         5, 
         4
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         10, 
         11
       ], 
       "pgid": "2.49", 
       "up": [
         10, 
         11
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         8, 
         9
       ], 
       "pgid": "2.50", 
       "up": [
         8, 
         9
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         11, 
         10
       ], 
       "pgid": "2.51", 
       "up": [
         11, 
         10
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         2, 
         3
       ], 
       "pgid": "2.52", 
       "up": [
         2, 
         3
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         9, 
         8
       ], 
       "pgid": "2.53", 
       "up": [
         9, 
         8
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         8, 
         9
       ], 
       "pgid": "2.54", 
       "up": [
         8, 
         9
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         7, 
         6
       ], 
       "pgid": "2.55", 
       "up": [
         7, 
         6
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         6, 
         7
       ], 
       "pgid": "2.56", 
       "up": [
         6, 
         7
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         1, 
         0
       ], 
       "pgid": "2.57", 
       "up": [
         1, 
         0
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         4, 
         5
       ], 
       "pgid": "2.58", 
       "up": [
         4, 
         5
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         7, 
         6
       ], 
       "pgid": "2.59", 
       "up": [
         7, 
         6
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         11, 
         10
       ], 
       "pgid": "2.60", 
       "up": [
         11, 
         10
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         0, 
         1
       ], 
       "pgid": "2.61", 
       "up": [
         0, 
         1
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         5, 
         4
       ], 
       "pgid": "2.62", 
       "up": [
         5, 
         4
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }, 
     {
       "acting": [
         10, 
         11
       ], 
       "pgid": "2.63", 
       "up": [
         10, 
         11
       ], 
       "state": [
         "active", 
         "clean"
       ]
     }
   ]

api/v2/cluster/cad0935f-e105-41db-8c71-4aa7c4602fb3/derived_object/counters
---------------------------------------------------------------------------

.. code-block:: json

   {
     "mds": {
       "up_not_in": 0, 
       "not_up_not_in": 0, 
       "total": 0, 
       "up_in": 0
     }, 
     "osd": {
       "warn": {
         "count": 0, 
         "states": {}
       }, 
       "critical": {
         "count": 0, 
         "states": {}
       }, 
       "ok": {
         "count": 12, 
         "states": {
           "up/in": 12
         }
       }
     }, 
     "pg": {
       "warn": {
         "count": 0, 
         "states": {}
       }, 
       "critical": {
         "count": 0, 
         "states": {}
       }, 
       "ok": {
         "count": 192, 
         "states": {
           "active": 192, 
           "clean": 192
         }
       }
     }, 
     "mon": {
       "warn": {
         "count": 0, 
         "states": {}
       }, 
       "critical": {
         "count": 0, 
         "states": {}
       }, 
       "ok": {
         "count": 3, 
         "states": {
           "in": 3
         }
       }
     }
   }

