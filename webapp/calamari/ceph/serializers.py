import sys
import time
import requests
from django.contrib.auth.models import User
from rest_framework import serializers
from ceph.models import Cluster

# This is the same routine we use in Kraken to fetch data from the cluster API.
# Here we are using it validate the URL provided by the user. We'll want to
# factor out some of the Kraken stuff to be re-usable, like this.
def _cluster_query(api_url, url):
    if api_url[-1] != '/':
        api_url += '/'
    hdr = {'accept': 'application/json'}
    r = requests.get(api_url + url, headers = hdr, timeout=5)
    return r.json()

class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cluster
        fields = ('name', 'api_base_url')

    def validate_api_base_url(self, attrs, source):
        try:
            data = _cluster_query(attrs[source], "status")
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
        fields = ('cluster', 'last_update', 'last_update_unix', 'name', 'health')

    def get_cluster(self, obj):
        return obj.id

    def get_last_update_unix(self, obj):
        return obj.last_update_unix
