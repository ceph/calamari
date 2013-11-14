import json
import requests


class AuthenticatedHttpClient(requests.Session):
    """
    Client for the calamari REST API, principally exists to do
    authentication, but also helpfully prefixes
    URLs in requests with the API base URL and JSONizes
    POST data.
    """
    def __init__(self, api_url, username, password):
        super(AuthenticatedHttpClient, self).__init__()
        self._username = username
        self._password = password
        self._api_url = api_url
        self.headers = {
            'Content-type': "application/json; charset=UTF-8"
        }

    def request(self, method, url, **kwargs):
        url = self._api_url + url
        return super(AuthenticatedHttpClient, self).request(method, url, **kwargs)

    def post(self, url, data=None, **kwargs):
        if isinstance(data, dict):
            data = json.dumps(data)
        super(AuthenticatedHttpClient, self).post(url, data, **kwargs)

    def login(self):
        """
        """
        response = self.get("auth/login/")
        response.raise_for_status()
        self.headers['X-XSRF-TOKEN'] = response.cookies['XSRF-TOKEN']

        self.post("auth/login/", {
            'next': "/",
            'username': self._username,
            'password': self._password
        })
        response.raise_for_status()

        # Check we're allowed in now.
        response = self.get("cluster")
        response.raise_for_status()
