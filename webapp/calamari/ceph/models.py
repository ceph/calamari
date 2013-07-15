from django.db import models
import jsonfield

class Cluster(models.Model):
    """
    A cluster being tracked by Calamari.
    """
    name = models.CharField(max_length=256)

    # REST API URL (e.g. monitor:port/api/v0.1)
    api_base_url = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class ClusterSpace(models.Model):
    """
    A snapshot of cluster space statistics.

    This roughly corresponds to `ceph df` without the per-pool statistics.
    """
    cluster = models.ForeignKey(Cluster)

    # Timestamp of collected statistics
    #
    # FIXME: Currently this corresponds to the time at which inserted the data
    # into the db. We could be really pedantic and have the cluster report to
    # us the time it was sampled.
    #
    added = models.DateTimeField(auto_now_add=True)

    # Raw report
    report = jsonfield.JSONField()

    class Meta:
        get_latest_by = "added"

class ClusterHealth(models.Model):
    """
    A snapshot of cluster health.
    """
    cluster = models.ForeignKey(Cluster)
    added = models.DateTimeField(auto_now_add=True)
    report = jsonfield.JSONField()

    class Meta:
        get_latest_by = "added"
