from django.db import models

class Cluster(models.Model):
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name

class SpaceUsage(models.Model):
    cluster = models.ForeignKey(Cluster)
    inserted = models.DateTimeField(auto_now_add=True)
    json_str = models.TextField()
