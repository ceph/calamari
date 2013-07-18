import sys
import time
from django.utils.dateformat import format
from django.contrib.auth.models import User
from rest_framework import serializers
from ceph.models import Cluster, ClusterSpace, ClusterHealth

class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cluster

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
    added_ms = serializers.SerializerMethodField('get_added_ms')

    class Meta:
        model = ClusterSpace

    def get_added_ms(self, obj):
        return format(obj.added, 'U')

class ClusterHealthSerializer(serializers.ModelSerializer):
    added_ms = serializers.SerializerMethodField('get_added_ms')

    class Meta:
        model = ClusterHealth

    def get_added_ms(self, obj):
        return format(obj.added, 'U')
