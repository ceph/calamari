from collections import defaultdict
import os
import json
import logging
logging.basicConfig()

from tests.server_testcase import ServerTestCase


class TestApi(ServerTestCase):
    def test_touch_urls(self):
        """
        This has two purposes:

        - To check that the touched URLs service GETs successfully
        - To store the returned structures for use as examples in the API documentation

        This is a slight intrusion of docs/build on the tests, but it's handy to have this inside
        the tests because the infrastructure for setting up a cluster and talking to it is already here.
        """

        # Unlike most of the integration tests, this one reaches inside the calamari
        # server code to introspect things.  Do this inside function scope so that
        # import errors are test errors rather than world-breakers.
        os.environ.setdefault("CALAMARI_CONFIG", "dev/calamari.conf")
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calamari_web.settings")
        from calamari_common.types import SYNC_OBJECT_TYPES
        from calamari_rest.management.commands.api_docs import ApiIntrospector

        url_patterns = ApiIntrospector("calamari_rest.urls.v2").get_url_list()
        from pprint import pprint
        pprint(url_patterns)

        # Spin up a running Calamari+Ceph environment
        self.ceph_ctl.configure(3)
        self.calamari_ctl.configure()
        fsid = self._wait_for_cluster()
        # Unlike most tests we really do need all the servers to be there in case
        # the one we're checking for isn't.
        self._wait_for_servers()

        # Pick a pool ID
        response = self.api.get("cluster/{0}/pool".format(fsid))
        response.raise_for_status()
        pool_id = response.json()[0]['id']

        # Make sure there is at least one request
        response = self.api.post("cluster/%s/pool" % (fsid), {'name': 'newname', 'pg_num': 64, 'pgp_num': 64})
        self.assertEqual(response.status_code, 202)
        request_id = response.json()['request_id']

        # Pick a user ID
        response = self.api.get("user")
        response.raise_for_status()
        user_id = response.json()[0]['id']

        # Pick a mon ID
        response = self.api.get("cluster/{0}/mon".format(fsid))
        response.raise_for_status()
        mon_id = response.json()[0]['name']

        # To go from URL patterns to something we can GET, substitute IDs from
        # the Ceph cluster we're running against
        replacements = {
            "<fsid>": [fsid],
            "<fqdn>": [self.ceph_ctl.get_server_fqdns()[0]],
            "<sync_type>": [s.str for s in SYNC_OBJECT_TYPES],
            "<osd_id>": ["0"],
            "<pool_id>": [str(pool_id)],
            "<node_id>": ["-1"],
            "server/<pk>": ["server/%s" % self.ceph_ctl.get_server_fqdns()[0]],
            "<minion_id>": [self.ceph_ctl.get_server_fqdns()[0]],
            "cluster/<pk>": ["cluster/%s" % fsid],
            "<request_id>": [request_id],
            "user/<pk>": ["user/{0}".format(user_id)],
            "<log_path>": ["ceph/ceph.log"],
            "config/<key>": ["config/mds_bal_interval"],
            "command/<command>": ["command/%s" % x for x in ("scrub", "deep_scrub", "repair")],
            "<mon_id>": [mon_id]
        }

        concrete_urls = {}
        for pat in url_patterns:
            urls = [pat]
            for pattern, options in replacements.items():
                new_urls = []
                for url in urls:
                    if pattern in url:
                        for option in options:
                            new_urls.append(url.replace(pattern, option))
                    else:
                        new_urls.append(url)

                urls = new_urls
            concrete_urls[pat] = urls

        # Dict of pattern to dict of concrete urls to response text
        prefix = "api/v2/"
        results = defaultdict(dict)
        fails = []
        for pattern, urls in concrete_urls.items():
            for url in urls:
                # *sigh* No Virginia, you don't use GET for modifications
                if 'auth/logout' in url:
                    continue
                response = self.api.get(url[len(prefix):])
                if response.status_code != 200:
                    fails.append((url, response.status_code, response.reason))
                    continue
                else:
                    results[pattern][url] = response.content

        self.assertListEqual(fails, [])

        open("api_examples.json", 'w').write(json.dumps(results))

    def test_touch_urls_in_a_404_way(self):

        # Unlike most of the integration tests, this one reaches inside the calamari
        # server code to introspect things.  Do this inside function scope so that
        # import errors are test errors rather than world-breakers.
        os.environ.setdefault("CALAMARI_CONFIG", "dev/calamari.conf")
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calamari_web.settings")
        from calamari_rest.management.commands.api_docs import ApiIntrospector

        # Spin up a running Calamari+Ceph environment
        self.ceph_ctl.configure(3)
        self.calamari_ctl.configure()
        fsid = self._wait_for_cluster()
        # Unlike most tests we really do need all the servers to be there in case
        # the one we're checking for isn't.
        self._wait_for_servers()

        url_patterns = ApiIntrospector("calamari_rest.urls.v2").get_url_list()
        only_urls_with_parameters = []
        for url in url_patterns:
            url = url.replace('<fsid>', fsid)
            if '<sync_type>' in url or 'config/<key>' in url:
                continue

            if url.find('<') != -1:
                only_urls_with_parameters.append(url)
        from pprint import pprint
        pprint(only_urls_with_parameters)

        url_patterns = only_urls_with_parameters

        # To go from URL patterns to something we can GET, substitute IDs from
        # the Ceph cluster we're running against
        replacements = {
            "<fqdn>": ["not.a.server"],
            "<osd_id>": ["12345"],
            "<pool_id>": ["12345"],
            "<node_id>": ["12345"],
            "server/<pk>": ["server/%s" % "not.a.server"],
            "<minion_id>": ["not.a.server"],
            "cluster/<pk>": ["cluster/12345"],
            "<request_id>": ["12345"],
            "user/<pk>": ["user/12345"],
            "<log_path>": ["ceph/ceph.log"],
            "command/<command>": ["command/%s" % x for x in ("scrub", "deep_scrub", "repair")],
            "<mon_id>": ["12345"]
        }

        concrete_urls = {}
        for pat in url_patterns:
            urls = [pat]
            for pattern, options in replacements.items():
                new_urls = []
                for url in urls:
                    if pattern in url:
                        for option in options:
                            new_urls.append(url.replace(pattern, option))
                    else:
                        new_urls.append(url)

                urls = new_urls
            concrete_urls[pat] = urls

        # Dict of pattern to dict of concrete urls to response text
        prefix = "api/v2/"
        fails = []
        for pattern, urls in concrete_urls.items():
            for url in urls:
                # *sigh* No Virginia, you don't use GET for modifications
                if 'auth/logout' in url:
                    continue
                response = self.api.get(url[len(prefix):])

                # We are mostly interested that these are not 500
                if response.status_code not in (404, 200, 503):
                    fails.append((url, response.status_code, response.reason))

                response = self.api.patch(url[len(prefix):], data={'status': 'accepted'})

                # We are mostly interested that these are not 500
                if response.status_code not in (400, 404, 405, 503):
                    fails.append((url, response.status_code, response.reason))

        from pprint import pprint
        pprint(fails)
        self.assertListEqual(fails, [])
