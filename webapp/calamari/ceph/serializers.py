from django.contrib.auth.models import User
from rest_framework import serializers
from ceph.models import Cluster, ClusterSpace

class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cluster
        fields = ('id', 'name')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')

    def convert_object(self, obj):
        if 'password' in self.fields:
            del self.fields['password']
        return super(UserSerializer, self).convert_object(obj)

    def restore_object(self, attrs, instance=None):
        user = super(UserSerializer, self).restore_object(attrs, instance)
        if user:
            user.set_password(attrs['password'])
        return user

class ClusterSpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClusterSpace
