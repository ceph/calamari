
Authentication
==============

The Calamari REST API uses the same username/password authentication method as the Calamari
user interface.

At a high level, given an HTTP client that supports cookies, the process is:

* GET any url, for example ``/api/v2/auth/login`` and use the XSRF-TOKEN cookie in the response
  as a the X-XSRF-TOKEN header on subsequent POSTs
* POST to ``/api/v2/auth/login``, with a JSON content of ``{'username': ..., 'password': ...}``
* Subsequent requests will be authenticated with a session cookie

For an example of how to authenticate with the API, please see the AuthenticatedHttpClient
class defined in the Calamari test suite: https://github.com/ceph/calamari/blob/master/tests/http_client.py

