from django.db import models

class Cluster(models.Model):
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name

class ClusterSpace(models.Model):
    cluster = models.ForeignKey(Cluster)
    # FIXME: make added_date not be auto-add; rather sample time
    added_date = models.DateTimeField(auto_now_add=True)
    total_space = models.BigIntegerField()
    total_avail = models.BigIntegerField()
    total_used = models.BigIntegerField()

    class Meta:
        get_latest_by = "added_date"
