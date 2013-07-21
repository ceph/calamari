Calamari RESTful API
=====

Documentation of the Calamari REST API exposed by the Calamari web service.
This is distinct from the Ceph REST API, a Ceph core service upon which
Calamari depends.

Calamari Information
-----

* **URL**: `info`
* **Method**: `GET`

```json
{
    "registered": "Inktank, Inc.", 
    "version": "0.1", 
    "ipaddr": "10.10.2.3", 
    "hostname": "calamari.inktank.com", 
    "license": "trial"
}
```

Authentication
-----

    auth/login
    auth/logout

User Management
-----

### User List

* **URL**: `user`
* **Method**: `GET`

#### Example Response

```json
[
    {
        "id": 1, 
        "username": "admin", 
    }, 
    {
        "id": 2, 
        "username": "noah", 
    }
]
```

### User Detail

* **URL**: `user/{id}`
* **Method**: `GET`

#### Example Response

```json
{
    "id": 1, 
    "username": "admin", 
}
```

Cluster Management
-----

### Cluster List

* **URL**: `cluster`
* **Method**: `GET`

#### Example Response

```json
[
    {
        "id": 1, 
        "name": "ceph", 
        "api_base_url": "http://ceph:3000/api/v0.1/"
    }, 
    {
        "id": 2, 
        "name": "hadoop", 
        "api_base_url": "http://hadoop:4000/api/v0.1/"
    }
]
```

### Cluster Detail

* **URL**: `cluster/{id}`
* **Method**: `GET`

#### Example Response

```json
{
    "id": 1, 
    "name": "ceph", 
    "api_base_url": "http://ceph:3000/api/v0.1/"
}
```

Cluster Space
-----

### Latest Report

* **URL**: `cluster/{id}/space`
* **Method**: `GET`

#### Example Response

```json
{
    "id": 1, 
    "cluster": 1, 
    "added_date": "2013-07-13T22:59:44.633Z", 
    "report": {
        "total_used": 53117004, 
        "total_space": 468345368, 
        "total_avail": 391437724
    }
}
```

Health Counters
-----

### Latest Report

* **URL**: `cluster/{id}/health_counters`
* **Method**: `GET`

#### Example Response

```json
{
    "osd": {
        "up_not_in": 1, 
        "not_up_not_in": 1, 
        "total": 70, 
        "up_in": 68
    }
}
```

Cluster Health
-----

### Latest Report

* **URL**: `cluster/{id}/health`
* **Method**: `GET`

#### Example Response (Simple, HEALTH_WARN)

```json
{
    "id": 1, 
    "cluster": 1, 
    "added_date": "2013-07-13T22:59:44.710Z", 
    "report": {
        "timechecks": {
            "round_status": "finished", 
            "epoch": 2, 
            "round": 0
        }, 
        "summary": [
            {
                "severity": "HEALTH_WARN", 
                "summary": "24 pgs degraded"
            }
        ], 
        "health": {
            "health_services": [
                {
                    "mons": [
                        {
                            "last_updated": "2013-07-13 15:58:15.581195", 
                            "name": "a", 
                            "avail_percent": 83, 
                            "kb_total": 468345368, 
                            "kb_avail": 391437748, 
                            "health": "HEALTH_OK", 
                            "kb_used": 53116980
                        }
                    ]
                }
            ]
        }, 
        "overall_status": "HEALTH_WARN", 
        "detail": []
    }
}
```

OSD List
-----

* **URL**: `cluster/{id}/osd`
* **Method**: `GET`

#### Example Response

```json
{
    "epoch": 5387, 
    "added": "2013-07-21T22:03:11.056Z", 
    "added_ms": 1374444191000, 
    "osds": [
        {
            "heartbeat_back_addr": "10.214.136.114:6810/8599", 
            "uuid": "4159311f-5127-4e05-88e5-33f526fe4417", 
            "heartbeat_front_addr": "10.214.136.114:6811/8599", 
            "down_at": 2534, 
            "up": 1, 
            "lost_at": 0, 
            "up_from": 2535, 
            "state": [
                "exists", 
                "up"
            ], 
            "last_clean_begin": 2512, 
            "last_clean_end": 2525, 
            "in": 1, 
            "public_addr": "10.214.136.114:6807/8599", 
            "up_thru": 10352, 
            "cluster_addr": "10.214.136.114:6808/8599", 
            "osd": 0
        }, 
    ]
}
```

OSD Detail
-----

* **URL**: `cluster/{id}/osd/{id}`
* **Method**: `GET`

#### Example Response

```json
{
    "added": "2013-07-21T22:04:12.210Z", 
    "added_ms": 1374444252000, 
    "osd": {
        "heartbeat_back_addr": "10.214.136.114:6814/8620", 
        "uuid": "ac9bb868-0990-40f0-a30f-62cd4ae4195e", 
        "heartbeat_front_addr": "10.214.136.114:6815/8620", 
        "down_at": 2533, 
        "up": 1, 
        "lost_at": 0, 
        "up_from": 2534, 
        "state": [
            "exists", 
            "up"
        ], 
        "last_clean_begin": 2511, 
        "last_clean_end": 2525, 
        "in": 1, 
        "public_addr": "10.214.136.114:6812/8620", 
        "up_thru": 10320, 
        "cluster_addr": "10.214.136.114:6813/8620", 
        "osd": 3
    }
}
```

OSD List Delta
-----

* **URL**: `cluster/{id}/osd/epoch/{id}`
* **Method**: `GET`

The `new`, `removed`, and `changed` lists are populated with the latest
versions of the OSD object.

#### Example Response

```json
{
    "added": "2013-07-21T22:11:51.915Z", 
    "added_ms": 1374444711000, 
    "changed": [], 
    "epoch": 5404, 
    "new": [], 
    "removed": []
}
```
