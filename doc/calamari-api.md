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
