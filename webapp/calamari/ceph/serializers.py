import sys
import time
import requests
from django.contrib.auth.models import User
from rest_framework import serializers
from ceph.models import Cluster
from ceph.management.commands.ceph_refresh import CephRestClient

class ClusterSerializer(serializers.ModelSerializer):
    cluster_update_time_unix = serializers.SerializerMethodField(
        'get_cluster_update_time_unix');
    cluster_update_attempt_time_unix = serializers.SerializerMethodField(
        'get_cluster_update_attempt_time_unix');
    class Meta:
        model = Cluster
        fields = ('id', 'name', 'api_base_url',
            'cluster_update_time', 'cluster_update_time_unix',
            'cluster_update_attempt_time', 'cluster_update_attempt_time_unix',
            'cluster_update_error_msg', 'cluster_update_error_isclient')

        # only kraken updates this stuff. we don't want to expose it through
        # the rest API, so these read-only fields won't be altered.
        read_only_fields = ('cluster_update_time',
            'cluster_update_attempt_time', 'cluster_update_error_msg',
            'cluster_update_error_isclient')

    def get_cluster_update_time_unix(self, obj):
        return obj.cluster_update_time_unix

    def get_cluster_update_attempt_time_unix(self, obj):
        return obj.cluster_update_attempt_time_unix

    def validate_api_base_url(self, attrs, source):
        try:
            # Will use the CephRestClient default connection timeout
            client = CephRestClient(attrs[source])
            data = client.get_health()
        except Exception:
            raise serializers.ValidationError("Could not contact the API URL provided.")
        return attrs

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the Django User model.

    Used to expose a django-rest-framework user management resource.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'password')

    def to_native(self, obj):
        # Before conversion, remove the password field. This prevents the hash
        # from being displayed when requesting user details.
        if 'password' in self.fields:
            del self.fields['password']
        return super(UserSerializer, self).to_native(obj)

    def restore_object(self, attrs, instance=None):
        user = super(UserSerializer, self).restore_object(attrs, instance)
        if user:
            # This will perform the Django-specific password obfuscation
            user.set_password(attrs['password'])
        return user

class ClusterSpaceSerializer(serializers.ModelSerializer):
    cluster = serializers.SerializerMethodField('get_cluster')
    cluster_update_time_unix = serializers.SerializerMethodField('get_cluster_update_time_unix')

    # backwards compatibility during transition
    report = serializers.SerializerMethodField('get_report')
    added = serializers.SerializerMethodField('get_added')
    added_ms = serializers.SerializerMethodField('get_cluster_update_time_unix')

    class Meta:
        model = Cluster
        fields = ('cluster', 'cluster_update_time', 'cluster_update_time_unix', 'space',
            'added', 'added_ms', 'report')

    def get_cluster(self, obj):
        return obj.id

    def get_cluster_update_time_unix(self, obj):
        return obj.cluster_update_time_unix

    def get_report(self, obj):
        return {
            'total_used': obj.space['used_bytes']/1024,
            'total_space': obj.space['capacity_bytes']/1024,
            'total_avail': obj.space['free_bytes']/1024,
        }

    def get_added(self, obj):
        return obj.cluster_update_time

class ClusterHealthSerializer(serializers.ModelSerializer):
    cluster = serializers.SerializerMethodField('get_cluster')
    cluster_update_time_unix = serializers.SerializerMethodField('get_cluster_update_time_unix')

    # backwards compatibility during transition
    report = serializers.SerializerMethodField('get_report')
    added = serializers.SerializerMethodField('get_added')
    added_ms = serializers.SerializerMethodField('get_cluster_update_time_unix')

    class Meta:
        model = Cluster
        fields = ('cluster', 'cluster_update_time', 'cluster_update_time_unix', 'report',
            'added', 'added_ms')

    def get_cluster(self, obj):
        return obj.id

    def get_cluster_update_time_unix(self, obj):
        return obj.cluster_update_time_unix

    def get_report(self, obj):
        return obj.health

    def get_added(self, obj):
        return obj.cluster_update_time

class ClusterHealthCountersSerializer(serializers.ModelSerializer):
    cluster = serializers.SerializerMethodField('get_cluster')
    cluster_update_time_unix = serializers.SerializerMethodField('get_cluster_update_time_unix')

    # backwards compatibility during transition
    report = serializers.SerializerMethodField('get_report')
    added = serializers.SerializerMethodField('get_added')
    added_ms = serializers.SerializerMethodField('get_cluster_update_time_unix')
    pg = serializers.SerializerMethodField('get_pg')
    mds = serializers.SerializerMethodField('get_mds')
    pool = serializers.SerializerMethodField('get_pool')
    mon = serializers.SerializerMethodField('get_mon')
    osd = serializers.SerializerMethodField('get_osd')

    class Meta:
        model = Cluster
        fields = ('cluster', 'cluster_update_time', 'cluster_update_time_unix',
            'added', 'added_ms', 'pg', 'mds', 'pool', 'mon', 'osd')

    def get_cluster(self, obj):
        return obj.id

    def get_cluster_update_time_unix(self, obj):
        return obj.cluster_update_time_unix

    def get_report(self, obj):
        return obj.health

    def get_added(self, obj):
        return obj.cluster_update_time

    def get_pg(self, obj):
        return obj.counters['pg']

    def get_mds(self, obj):
        return obj.counters['mds']

    def get_pool(self, obj):
        return obj.counters['pool']

    def get_mon(self, obj):
        return obj.counters['mon']

    def get_osd(self, obj):
        return obj.counters['osd']

class OSDListSerializer(serializers.ModelSerializer):
    cluster = serializers.SerializerMethodField('get_cluster')
    cluster_update_time_unix = serializers.SerializerMethodField('get_cluster_update_time_unix')
    pg_state_counts = serializers.SerializerMethodField('get_pg_state_counts')

    # backwards compatibility during transition
    added = serializers.SerializerMethodField('get_added')
    added_ms = serializers.SerializerMethodField('get_cluster_update_time_unix')
    epoch = serializers.SerializerMethodField('get_epoch')
    osds = serializers.SerializerMethodField('get_osds')

    class Meta:
        model = Cluster
        fields = ('cluster', 'cluster_update_time', 'cluster_update_time_unix', 'osds',
            'added', 'added_ms', 'epoch', 'pg_state_counts')

    def get_cluster(self, obj):
        return obj.id

    def get_osds(self, obj):
        if obj.osds:
            for osd in obj.osds:
                osd['osd'] = osd['id']
        return obj.osds

    def get_cluster_update_time_unix(self, obj):
        return obj.cluster_update_time_unix

    def get_added(self, obj):
        return obj.cluster_update_time

    def get_epoch(self, obj):
        return 0

    def get_pg_state_counts(self, obj):
        return dict((s, len(v)) for s, v in obj.osds_by_pg_state.iteritems())

class OSDDetailSerializer(serializers.ModelSerializer):
    cluster = serializers.SerializerMethodField('get_cluster')
    cluster_update_time_unix = serializers.SerializerMethodField('get_cluster_update_time_unix')
    osd = serializers.SerializerMethodField('get_osd')

    # backwards compatibility during transition
    added = serializers.SerializerMethodField('get_added')
    added_ms = serializers.SerializerMethodField('get_cluster_update_time_unix')

    def __init__(self, cluster, osd_id, *args, **kwargs):
        self.osd_id = osd_id
        super(OSDDetailSerializer, self).__init__(cluster, *args, **kwargs)

    class Meta:
        model = Cluster
        fields = ('cluster', 'cluster_update_time', 'cluster_update_time_unix', 'osd',
            'added', 'added_ms')

    def get_cluster(self, obj):
        return obj.id

    def get_cluster_update_time_unix(self, obj):
        return obj.cluster_update_time_unix

    def get_osd(self, obj):
        osd = obj.get_osd(self.osd_id)
        # backwards compat during transition
        osd['osd'] = osd['id']
        return osd

    def get_added(self, obj):
        return obj.cluster_update_time
