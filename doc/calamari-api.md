Calamari RESTful API
=====

Documentation of the Calamari REST API exposed by the Calamari web service.
This is distinct from the Ceph REST API, a Ceph core service upon which
Calamari depends.

Authentication
-----

    auth/login/
    auth/logout/

User Management
-----

### User List

* **URL**: `user/`
* **Method**: `GET`

#### Example Response

```json
[
    {
        "id": 1, 
        "username": "admin", 
        "password": "pbkdf2_sha256$10000$r9rj3Q0x1dQY$7QIH/3eGAe52R/xdobwaUN92WsyB4JgkC9x0M6Yfflw="
    }, 
    {
        "id": 2, 
        "username": "noah", 
        "password": "pbkdf2_sha256$10000$ghVVq1Q2fwmG$IU2F9E+x1oTDmciXOG9sEy/0KzB9PlPieGPQi3AWgxM="
    }
]
```

### User Detail

* **URL**: `user/{id}/`
* **Method**: `GET`

#### Example Response

```json
{
    "id": 1, 
    "username": "admin", 
    "password": "pbkdf2_sha256$10000$r9rj3Q0x1dQY$7QIH/3eGAe52R/xdobwaUN92WsyB4JgkC9x0M6Yfflw="
}
```

Cluster Management
-----

### Cluster List

* **URL**: `cluster/`
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

* **URL**: `cluster/{id}/space/`
* **Method**: `GET`

#### Example Response

```json
{
    "id": 2, 
    "cluster": 2, 
    "added_date": "2013-07-11T18:46:13.465Z", 
    "total_space": 982739, 
    "total_avail": 9849030, 
    "total_used": 8832356
}
```
