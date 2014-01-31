from collections import defaultdict
import sys
import os
import json

from django.core.management import execute_from_command_line
from StringIO import StringIO
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
        from cthulhu.manager.types import SYNC_OBJECT_TYPES
        from cthulhu.manager import derived
        from ceph.management.commands.api_docs import ApiIntrospector

        url_list_buffer = StringIO()

        # Run 'api_doc --list-urls' to get the API docs view of what URLs exist
        old_stdout = sys.stdout
        sys.stdout = url_list_buffer
        execute_from_command_line(["", "api_docs", "--list-urls"])
        sys.stdout.flush()
        sys.stdout = old_stdout
        url_patterns = json.loads(url_list_buffer.getvalue())

        url_patterns = ApiIntrospector("ceph.urls.v2").get_url_list()

        # Spin up a running Calamari+Ceph environment
        self.ceph_ctl.configure(3)
        self.calamari_ctl.configure()
        fsid = self._wait_for_cluster()
        # Unlike most tests we really do need all the servers to be there in case
        # the one we're checking for isn't.
        self._wait_for_servers()

        # Make sure there is at least one request
        response = self.api.patch("cluster/%s/pool/0" % fsid, {'name': 'newname'})
        self.assertEqual(response.status_code, 202)
        request_id = response.json()['request_id']

        # To go from URL patterns to something we can GET, substitute IDs from
        # the Ceph cluster we're running against
        replacements = {
            "<fsid>": [fsid],
            "<fqdn>": [self.ceph_ctl.get_server_fqdns()[0]],
            "<sync_type>": [s.str for s in SYNC_OBJECT_TYPES],
            "<derived_type>": [p for d in derived.generators for p in d.provides],
            "<osd_id>": ["0"],
            "<pool_id>": ["0"],
            "server/<pk>": ["server/%s" % self.ceph_ctl.get_server_fqdns()[0]],
            "key/<pk>": ["key/%s" % self.ceph_ctl.get_server_fqdns()[0]],
            "cluster/<pk>": ["cluster/%s" % fsid],
            "<request_id>": [request_id],
            "user/<pk>": ["user/1"],
            "<log_path>": "ceph/ceph.log",

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
                    fails.append(url)
                    continue
                else:
                    results[pattern][url] = response.content

        self.assertListEqual(fails, [])

        open("api_examples.json", 'w').write(json.dumps(results))
