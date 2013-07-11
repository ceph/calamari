from django.db import models

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
    added_date = models.DateTimeField(auto_now_add=True)

    # Tracked statistics in bytes
    total_space = models.BigIntegerField()
    total_avail = models.BigIntegerField()
    total_used = models.BigIntegerField()

    class Meta:
        get_latest_by = "added_date"
