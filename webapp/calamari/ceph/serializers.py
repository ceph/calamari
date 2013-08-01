import sys
import time
import requests
from django.contrib.auth.models import User
from rest_framework import serializers
from ceph.models import Cluster
from ceph.management.commands.ceph_refresh import CephRestClient

class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cluster
        fields = ('name', 'api_base_url')

    def validate_api_base_url(self, attrs, source):
        try:
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
    last_update_unix = serializers.SerializerMethodField('get_last_update_unix')

    class Meta:
        model = Cluster
        fields = ('cluster', 'last_update', 'last_update_unix', 'name', 'space')

    def get_cluster(self, obj):
        return obj.id

    def get_last_update_unix(self, obj):
        return obj.last_update_unix

class ClusterHealthSerializer(serializers.ModelSerializer):
    cluster = serializers.SerializerMethodField('get_cluster')
    last_update_unix = serializers.SerializerMethodField('get_last_update_unix')

    class Meta:
        model = Cluster
        fields = ('cluster', 'last_update', 'last_update_unix', 'health', 'counters')

    def get_cluster(self, obj):
        return obj.id

    def get_last_update_unix(self, obj):
        return obj.last_update_unix

class OSDListSerializer(serializers.ModelSerializer):
    cluster = serializers.SerializerMethodField('get_cluster')
    last_update_unix = serializers.SerializerMethodField('get_last_update_unix')

    class Meta:
        model = Cluster
        fields = ('cluster', 'last_update', 'last_update_unix', 'osds')

    def get_cluster(self, obj):
        return obj.id

    def get_last_update_unix(self, obj):
        return obj.last_update_unix

class OSDDetailSerializer(serializers.ModelSerializer):
    cluster = serializers.SerializerMethodField('get_cluster')
    last_update_unix = serializers.SerializerMethodField('get_last_update_unix')
    osd = serializers.SerializerMethodField('get_osd')

    def __init__(self, cluster, osd_id, *args, **kwargs):
        self.osd_id = osd_id
        super(OSDDetailSerializer, self).__init__(cluster, *args, **kwargs)

    class Meta:
        model = Cluster
        fields = ('cluster', 'last_update', 'last_update_unix', 'osd')

    def get_cluster(self, obj):
        return obj.id

    def get_last_update_unix(self, obj):
        return obj.last_update_unix

    def get_osd(self, obj):
        return obj.get_osd(self.osd_id)
