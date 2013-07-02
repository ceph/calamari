from django.http import Http404
from ceph.models import Cluster
from ceph.serializers import ClusterSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

class ClusterList(APIView):
    queryset = Cluster.objects.all()

    def get(self, request, format=None):
        clusters = Cluster.objects.all()
        serializer = ClusterSerializer(clusters, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ClusterSerializer(data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClusterDetail(APIView):
    queryset = Cluster.objects.all()

    def get_object(self, pk):
        try:
            return Cluster.objects.get(pk=pk)
        except Cluster.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        cluster = self.get_object(pk)
        serializer = ClusterSerializer(cluster)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        cluster = self.get_object(pk)
        serializer = ClusterSerializer(cluster, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        cluster = self.get_object(pk)
        cluster.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
