from rest_framework import serializers
from ceph.models import Cluster

class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cluster
        fields = ('id', 'name')
