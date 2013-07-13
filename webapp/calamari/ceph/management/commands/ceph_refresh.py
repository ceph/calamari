import traceback
import requests
from django.core.management.base import BaseCommand, CommandError
from ceph.models import Cluster, ClusterSpace, ClusterHealth

class Command(BaseCommand):
    """
    Administrative function for refreshing Ceph cluster stats.

    The `ceph_refresh` command will attempt to update statistics for each
    registered cluster found in the database.

    A failure that occurs while updating cluster statistics will abort the
    refresh for that cluster. An attempt will be made for other clusters.
    """
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self._last_response = None    # last cluster query response

    def handle(self, *args, **options):
        """
        Update statistics for each registered cluster.
        """
        clusters = Cluster.objects.all()
        for cluster in clusters:
            self.stdout.write("Refreshing data from cluster: %s (%s)" % \
                    (cluster.name, cluster.api_base_url))
            try:
                self._refresh_cluster_space(cluster)
                self._refresh_cluster_health(cluster)
            except Exception as e:
                # dump context from the last cluster query response
                self._print_response(self.stderr, self._last_response)
                self.stderr.write(traceback.format_exc())

    def _print_response(self, out, r):
        """
        Print out requests.py Response object information.
        """
        if not r:
            out.write("last response: <not set>")
            return
        out.write("last response: status code: %d" % (r.status_code,))
        out.write("last response: headers: %s" % (r.headers,))
        out.write("last response: content: %s" % (r.text,))

    def _cluster_query(self, cluster, url):
        """
        Fetch a JSON result for a Ceph REST API target.
        """
        url_base = cluster.api_base_url
        if url_base[-1] != '/':
            url_base.append('/')
        hdr = {'accept': 'application/json'}
        r = requests.get(url_base + url, headers = hdr)
        self._last_response = r
        return r.json()

    def _refresh_cluster_space(self, cluster):
        """
        Update cluster space statistics.
        """
        result = self._cluster_query(cluster, "df")
        cluster_stats = result['output']['stats']
        ClusterSpace(cluster=cluster, space=cluster_stats).save()
        self.stdout.write("(%s): updated cluster space stats" % (cluster.name,))

    def _refresh_cluster_health(self, cluster):
        """
        Update cluster health.
        """
        result = self._cluster_query(cluster, "health")
        ClusterHealth(cluster=cluster, health=result['output']).save()
        self.stdout.write("(%s): updated cluster health" % (cluster.name,))
