from django.utils import dateformat
from django.db import models
import jsonfield

import pytz


def get_latest(metric):
    # Local imports so that this module can be imported outside a django
    # app (the graphite imports look for settings.*)
    from graphite.render.attime import parseATTime
    from graphite.render.datalib import fetchData

    tzinfo = pytz.timezone("UTC")
    until_time = parseATTime('now', tzinfo)
    from_time = parseATTime('-10min', tzinfo)
    series = fetchData({
        'startTime': from_time,
        'endTime': until_time,
        'localOnly': False},
        metric
    )
    try:
        return [k for k in series[0] if k is not None][-1]
    except IndexError:
        return None


class Cluster(models.Model):
    """
    A cluster being tracked by Calamari.
    """
    name = models.CharField(max_length=256, unique=True)

    # FIXME put in proper max-length for a fsid
    #fsid = models.CharField(max_length=256, unique=True)

    api_base_url = models.CharField(max_length=200)

    # last time kraken ran
    cluster_update_attempt_time = models.DateTimeField(blank=True, null=True)

    # last time kraken successfully updated this cluster
    cluster_update_time = models.DateTimeField(blank=True, null=True)

    # message regarding the last error that occured (e.g. an exception stack
    # trace). This is cleared after any successful update.
    cluster_update_error_msg = models.TextField(blank=True, null=True)

    # true if the last kraken error occurred while communicating with the
    # cluster REST api.
    cluster_update_error_isclient = models.NullBooleanField(blank=True, null=True)

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
    #space = jsonfield.JSONField(null=True)
    health = jsonfield.JSONField(null=True)
    osds = jsonfield.JSONField(null=True)
    osds_by_pg_state = jsonfield.JSONField(null=True)
    counters = jsonfield.JSONField(null=True)
    pgs = jsonfield.JSONField(null=True)

    def __unicode__(self):
        return self.name

    def _convert_to_unix_ms(self, t):
        if t is None:
            return None
        return int(dateformat.format(t, 'U')) * 1000

    def _get_cluster_update_time_ms(self):
        """Convert `cluster_update_time` into Unix time."""
        return self._convert_to_unix_ms(self.cluster_update_time)

    def _get_cluster_update_attempt_time_ms(self):
        """Convert `cluster_update_attempt_time` into Unix time."""
        return self._convert_to_unix_ms(self.cluster_update_time)

    cluster_update_time_unix = property(_get_cluster_update_time_ms)
    cluster_update_attempt_time_unix = property(_get_cluster_update_attempt_time_ms)

    def get_osd(self, osd_id):
        if not self.osds:
            return None
        for osd in self.osds:
            if osd['id'] == int(osd_id):
                return osd
        return None

    def has_osd(self, osd_id):
        return self.get_osd(osd_id) is not None

    @property
    def space(self):
        def to_bytes(kb):
            if kb is not None:
                return kb * 1024
            else:
                return None

        df_path = lambda stat_name: "ceph.{0}.df.{1}".format(self.name, stat_name)
        return {
            'used_bytes': to_bytes(get_latest(df_path('total_used'))),
            'capacity_bytes': to_bytes(get_latest(df_path('total_space'))),
            'free_bytes': to_bytes(get_latest(df_path('totaL_avail')))
        }