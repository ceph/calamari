from django.utils import dateformat
from django.db import models
import jsonfield

class Cluster(models.Model):
    """
    A cluster being tracked by Calamari.
    """
    name = models.CharField(max_length=256, unique=True)
    last_update = models.DateTimeField(auto_now=True)
    api_base_url = models.CharField(max_length=200)

    #
    # Cluster state ready to be served up by the Calamari API.
    # 
    # These fields are populated by Kraken by performing any conversions from
    # the raw form, and as a side effect, validate the input.  Note that we
    # could store the raw data, but we'd rather throw an error at the Kraken
    # level if raw data is malformed and have stale data in the DB, than risk
    # having a cascading effect of problems with different components
    # expecting a certain schema if we were to blindly serve the raw data. We
    # can also choose to store the raw data, but this particular model seems
    # to maximize the decoupling between the particular web-framework being
    # used, and the extraction of knowledge from the cluster API. All of this
    # will probably be deleted and rewritten in the near future any way :).
    #
    space = jsonfield.JSONField(null=True)
    health = jsonfield.JSONField(null=True)
    osds = jsonfield.JSONField(null=True)
    counters = jsonfield.JSONField(null=True)

    def __unicode__(self):
        return self.name

    def _get_last_update_ms(self):
        "Convert `last_update` into Unix time."
        return int(dateformat.format(self.last_update, 'U')) * 1000

    last_update_unix = property(_get_last_update_ms)

    def get_osd(self, osd_id):
        if not self.osds:
            return None
        for osd in self.osds:
            if osd['id'] == int(osd_id):
                return osd
        return None

    def has_osd(self, osd_id):
        return self.get_osd(osd_id) is not None
